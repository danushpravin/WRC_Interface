"""
WRC Client Stream Script

Usage:
    python stream.py                           # raw mode, camera 0
    python stream.py --mode processed          # HSV processing
    python stream.py --camera 1                # use USB cam
    python stream.py --server http://192.168.x.x:8000  # remote server
"""

import argparse
import asyncio
import time
import random
import string

import cv2
import numpy as np
import requests
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame





# --- Custom video track that reads from OpenCV ---
class CameraTrack(VideoStreamTrack):
    def __init__(self, camera_index: int):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        self.frame_times = []
        self.latencies = []

        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}")

        print(f"Camera {camera_index} opened ")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera")

        start = time.time()

       

        latency = (time.time() - start) * 1000
        # store metrics (NO PRINTING HERE)
        self.latencies.append(latency)
        if len(self.latencies) > 100:
            self.latencies.pop(0)
        
        now = time.time()
        self.frame_times.append(now)
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)


        # Convert to RGB for WebRTC
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame
    
    async def metrics_loop(self):
        while True:
            await asyncio.sleep(1)

            if len(self.frame_times) >= 2:
                fps = len(self.frame_times) / (
                    self.frame_times[-1] - self.frame_times[0]
                )
            else:
                fps = 0

            avg_latency = (
                sum(self.latencies) / len(self.latencies)
                if self.latencies else 0
            )

            print(f"[METRICS] FPS: {fps:.2f} | Avg latency: {avg_latency:.2f} ms")

    def stop(self):
        self.cap.release()
        super().stop()



async def run(server_url: str, camera_index: int):
    pc = RTCPeerConnection()
    track = CameraTrack(camera_index)
    pc.addTrack(track)

    asyncio.create_task(track.metrics_loop())

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Wait for ICE gathering
    while pc.iceGatheringState != "complete":
        await asyncio.sleep(0.1)

    webrtc_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    print(f"Connecting to {server_url}/webrtc/offer ...")

    response = requests.post(
        f"{server_url}/webrtc/offer",
        json={
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
            "webrtc_id": webrtc_id,
        }
    )

    answer_data = response.json()

    if answer_data.get("status") == "failed":
        print(f"Connection failed: {answer_data['meta']['error']}")
        return

    answer = RTCSessionDescription(sdp=answer_data["sdp"], type=answer_data["type"])
    await pc.setRemoteDescription(answer)

    print("Connected! Streaming... Press Ctrl+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping stream...")
    finally:
        track.stop()
        await pc.close()


def main():
    parser = argparse.ArgumentParser(description="WRC Camera Stream Client")
    parser.add_argument("--server", default="http://localhost:8000")
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()

    print(f"Starting — server: {args.server}, camera: {args.camera}")
    asyncio.run(run(args.server, args.camera))


if __name__ == "__main__":
    main()