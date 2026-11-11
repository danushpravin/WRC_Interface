from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.modules.slots.schemas import SlotCreateRequest
from app.modules.slots.service import create_slot
from app.core.database import get_db
from app.modules.arenas.service import get_all_arenas
from app.modules.games.service import get_all_games
from app.modules.slots.service import get_all_slots, get_slot_by_id, get_registrations_with_users
from app.modules.sessions.service import get_session_by_id
from app.modules.leaderboards.service import get_leaderboard
from app.modules.auth.service import register_user, login_user
from app.modules.auth.schemas import RegisterRequest, LoginRequest
from app.core.security import decode_access_token
from app.modules.users.models import User
from app.modules.slots.service import register_for_slot, cancel_registration
from app.modules.arenas.service import get_arena_by_slug
from app.modules.games.models import GameVariant
from app.modules.arenas.models import Arena
from app.modules.sessions.service import (
    get_session_by_id,
    start_session,
    pause_session,
    resume_session,
    complete_session,
    fault_session,
)
from app.modules.sessions.schemas import SessionResultRequest
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["pages"])


def get_session_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    return db.query(User).filter(User.id == int(payload["sub"])).first()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "session_user": user,
    })


@router.get("/games", response_class=HTMLResponse)
def games_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    games = get_all_games(db)
    return templates.TemplateResponse("games.html", {
        "request": request,
        "session_user": user,
        "games": games,
    })


@router.get("/arenas", response_class=HTMLResponse)
def arenas_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    arenas = get_all_arenas(db)
    return templates.TemplateResponse("arenas.html", {
        "request": request,
        "session_user": user,
        "arenas": arenas,
    })


@router.get("/slots", response_class=HTMLResponse)
def slots_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    slots = get_all_slots(db)
    return templates.TemplateResponse("slots.html", {
        "request": request,
        "session_user": user,
        "slots": slots,
    })

@router.get("/slots/{slot_id}", response_class=HTMLResponse)
def slot_detail_page(slot_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    slot = get_slot_by_id(slot_id, db)
    if not slot:
        return templates.TemplateResponse("404.html", {"request": request, "session_user": user})
    registrations = get_registrations_with_users(slot_id, db)
    arena = db.query(Arena).filter(Arena.id == slot.arena_id).first()
    variant = db.query(GameVariant).filter(GameVariant.id == slot.game_variant_id).first()
    return templates.TemplateResponse("slot_detail.html", {
        "request": request,
        "session_user": user,
        "slot": slot,
        "registrations": registrations,
        "arena": arena,
        "variant": variant,
    })

@router.post("/slots/{slot_id}/register")
def slot_register_post(slot_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    try:
        register_for_slot(slot_id, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/slots/{slot_id}", status_code=302)

@router.post("/slots/{slot_id}/cancel")
def slot_cancel_post(slot_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    try:
        cancel_registration(slot_id, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/slots/{slot_id}", status_code=302)


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
def session_page(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    session = get_session_by_id(session_id, db)
    if not session:
        return templates.TemplateResponse("404.html", {"request": request, "session_user": user})
    return templates.TemplateResponse("session.html", {
        "request": request,
        "session_user": user,
        "session": session,
    })


@router.get("/leaderboards", response_class=HTMLResponse)
def leaderboards_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    racing = get_leaderboard("robot_racing", "global", db)
    football = get_leaderboard("robot_football", "global", db)
    return templates.TemplateResponse("leaderboards.html", {
        "request": request,
        "session_user": user,
        "racing": racing,
        "football": football,
    })


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "session_user": None})


@router.post("/login", response_class=HTMLResponse)
def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        result = login_user(LoginRequest(email=email, password=password), db)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("access_token", result["access_token"], httponly=True)
        return response
    except ValueError as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "session_user": None,
            "error": str(e),
        })


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "session_user": None})


@router.post("/register", response_class=HTMLResponse)
def register_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    gamer_name: str = Form(...),
    country_code: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        register_user(RegisterRequest(
            email=email,
            password=password,
            gamer_name=gamer_name,
            country_code=country_code or None,
        ), db)
        return RedirectResponse(url="/login", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "session_user": None,
            "error": str(e),
        })


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/admin/slots", response_class=HTMLResponse)
def admin_slots_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    slots = get_all_slots(db)
    arenas = get_all_arenas(db)
    games = get_all_games(db)
    return templates.TemplateResponse("admin_slots.html", {
        "request": request,
        "session_user": user,
        "slots": slots,
        "arenas": arenas,
        "games": games,
    })

@router.post("/admin/slots/create")
def admin_create_slot(
    request: Request,
    arena_id: int = Form(...),
    game_variant_id: int = Form(...),
    starts_at: str = Form(...),
    ends_at: str = Form(...),
    capacity: int = Form(...),
    price_tokens: float = Form(0),
    wagering_allowed: str = Form("false"),
    db: Session = Depends(get_db),
):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)

    data = SlotCreateRequest(
        arena_id=arena_id,
        game_variant_id=game_variant_id,
        starts_at=datetime.fromisoformat(starts_at),
        ends_at=datetime.fromisoformat(ends_at),
        capacity=capacity,
        price_tokens=price_tokens,
        wagering_allowed=(wagering_allowed == "true"),
    )
    create_slot(data, user, db)
    return RedirectResponse(url="/admin/slots", status_code=302)


@router.get("/admin/sessions/{session_id}", response_class=HTMLResponse)
def admin_session_page(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    session = get_session_by_id(session_id, db)
    if not session:
        return templates.TemplateResponse("404.html", {"request": request, "session_user": user})
    return templates.TemplateResponse("admin_session.html", {
        "request": request,
        "session_user": user,
        "session": session,
    })

@router.post("/admin/sessions/{session_id}/start")
def admin_start_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    try:
        start_session(session_id, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=302)


@router.post("/admin/sessions/{session_id}/pause")
def admin_pause_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    try:
        pause_session(session_id, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=302)


@router.post("/admin/sessions/{session_id}/resume")
def admin_resume_session(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    try:
        resume_session(session_id, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=302)


@router.post("/admin/sessions/{session_id}/fault")
def admin_fault_session(session_id: int, request: Request, reason: str = Form("admin_fault"), db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    try:
        fault_session(session_id, reason, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=302)


@router.post("/admin/sessions/{session_id}/complete")
def admin_complete_session(
    session_id: int,
    request: Request,
    result_code: str = Form(...),
    end_reason: str = Form(...),
    winning_user_id: str = Form(""),
    result_payload_json: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    data = SessionResultRequest(
        result_code=result_code,
        winning_user_id=int(winning_user_id) if winning_user_id else None,
        end_reason=end_reason,
        result_payload_json=result_payload_json or None,
    )
    try:
        complete_session(session_id, data, user, db)
    except ValueError:
        pass
    return RedirectResponse(url=f"/admin/sessions/{session_id}", status_code=302)

@router.get("/tournaments", response_class=HTMLResponse)
def tournaments_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    return templates.TemplateResponse("tournaments.html", {
        "request": request,
        "session_user": user,
    })

@router.get("/account/wallet", response_class=HTMLResponse)
def wallet_page(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("account_wallet.html", {
        "request": request,
        "session_user": user,
    })

@router.get("/admin/sessions/{session_id}/stream", response_class=HTMLResponse)
def admin_stream_page(session_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("admin_stream.html", {
        "request": request,
        "session_user": user,
        "session_id": session_id,
    })

@router.post("/admin/slots/{slot_id}/create-session")
def admin_create_session(slot_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    slot = get_slot_by_id(slot_id, db)
    if not slot:
        return RedirectResponse(url="/admin/slots", status_code=302)
    from app.modules.sessions.service import create_session
    from app.modules.sessions.schemas import SessionCreateRequest
    data = SessionCreateRequest(
        slot_id=slot_id,
        arena_id=slot.arena_id,
        game_variant_id=slot.game_variant_id,
        wagering_enabled=slot.wagering_allowed,
    )
    session = create_session(data, user, db)
    return RedirectResponse(url=f"/admin/sessions/{session.id}/stream", status_code=302)

@router.post("/admin/stream/start")
def admin_stream_start(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    from app.core.stream_state import stream_state
    if not stream_state.client_connected:
        return RedirectResponse(url="/", status_code=302)
    stream_state.game_active = True
    return RedirectResponse(request.headers.get("referer", "/"), status_code=302)


@router.post("/admin/stream/stop")
def admin_stream_stop(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    from app.core.stream_state import stream_state
    stream_state.game_active = False
    return RedirectResponse(request.headers.get("referer", "/"), status_code=302)

@router.post("/admin/stream/mode")
def admin_stream_mode(request: Request, mode: str = Form("processed"), db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user or user.role.value not in ("admin", "super_admin"):
        return RedirectResponse(url="/login", status_code=302)
    from app.core.stream_state import stream_state
    if mode in ("raw", "processed"):
        stream_state.stream_mode = mode
    return RedirectResponse(request.headers.get("referer", "/"), status_code=302)