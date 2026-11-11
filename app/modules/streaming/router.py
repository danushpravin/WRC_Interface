import asyncio
import json
import time

import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.dependencies import require_admin
from app.core.stream_state import stream_state

router = APIRouter(tags=["streaming"])

pcs = set()


def detect_ball(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([20, 100, 100])
    upper = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 10:
            cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            cv2.circle(img, (int(x), int(y)), 3, (0, 0, 255), -1)
            cv2.putText(img, f"ball ({int(x)},{int(y)})",
                        (int(x) - 40, int(y) - int(radius) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img


async def receive_frames(track):
    while True:
        try:
            frame = await track.recv()
            img = frame.to_ndarray(format="bgr24")
            if stream_state.stream_mode == "processed":
                img = detect_ball(img)
            async with stream_state.lock:
                stream_state.latest_frame = img
        except Exception as e:
            print(f"Frame receive error: {e}")
            stream_state.client_connected = False
            stream_state.latest_frame = None
            break


@router.post("/webrtc/offer")
async def webrtc_offer(request: Request):
    body = await request.json()
    offer = RTCSessionDescription(sdp=body["sdp"], type=body["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "connected":
            stream_state.client_connected = True
        elif pc.connectionState in ("disconnected", "failed", "closed"):
            stream_state.client_connected = False
            stream_state.latest_frame = None
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            asyncio.ensure_future(receive_frames(track))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


@router.post("/admin/stream/start")
def stream_start(current_user=Depends(require_admin)):
    if not stream_state.client_connected:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No client connected")
    stream_state.game_active = True
    return {"status": "started"}


@router.post("/admin/stream/stop")
def stream_stop(current_user=Depends(require_admin)):
    stream_state.game_active = False
    return {"status": "stopped"}


@router.post("/admin/stream/mode")
async def stream_mode(request: Request, current_user=Depends(require_admin)):
    body = await request.json()
    mode = body.get("mode", "raw")
    if mode not in ("raw", "processed"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid mode")
    stream_state.stream_mode = mode
    return {"status": "ok", "mode": mode}


@router.get("/stream/status")
async def stream_status(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            data = {
                "client_connected": stream_state.client_connected,
                "game_active": stream_state.game_active,
                "stream_mode": stream_state.stream_mode,
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/stream/feed")
async def stream_feed():
    async def frame_generator():
        while True:
            if not stream_state.game_active:
                await asyncio.sleep(0.1)
                continue
            if stream_state.latest_frame is None:
                await asyncio.sleep(0.1)
                continue
            async with stream_state.lock:
                frame = stream_state.latest_frame.copy()
            _, jpeg = cv2.imencode(".jpg", frame)
            frame_bytes = jpeg.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame_bytes +
                b"\r\n"
            )
            await asyncio.sleep(0.033)
    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )