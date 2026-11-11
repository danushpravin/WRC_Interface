from app.core.database import SessionLocal
from app.modules.users.models import User, UserRole, UserStatus
from app.modules.arenas.models import Arena, ArenaCapabilities, ArenaStatus
from app.modules.games.models import Game, GameVariant, GameStatus
from app.core.security import hash_password

def seed():
    db = SessionLocal()
    try:
        # Users
        admin = User(
            email="admin@wrc.com",
            password_hash=hash_password("admin1234"),
            gamer_name="admin",
            role=UserRole.admin,
            country_code="GBR",
            status=UserStatus.active,
        )
        player1 = User(
            email="player1@test.com",
            password_hash=hash_password("player1234"),
            gamer_name="SpeedDemon99",
            role=UserRole.player,
            country_code="GBR",
            status=UserStatus.active,
        )
        insider = User(
            email="insider@wrc.com",
            password_hash=hash_password("player1234"),
            gamer_name="InsiderBot1",
            role=UserRole.insider_player,
            is_insider_player=True,
            country_code="GBR",
            status=UserStatus.active,
        )
        db.add_all([admin, player1, insider])
        db.flush()

        # Arenas
        arena_london = Arena(
            name="WRC London Arena",
            slug="wrc-london",
            country_code="GBR",
            city="London",
            timezone="Europe/London",
            status=ArenaStatus.active,
            description="Flagship London arena. Wagering enabled.",
        )
        arena_mumbai = Arena(
            name="WRC Mumbai Arena",
            slug="wrc-mumbai",
            country_code="IND",
            city="Mumbai",
            timezone="Asia/Kolkata",
            status=ArenaStatus.active,
            description="Mumbai arena. Wagering not available in this region.",
        )
        db.add_all([arena_london, arena_mumbai])
        db.flush()

        db.add(ArenaCapabilities(
            arena_id=arena_london.id,
            wagering_enabled=True,
            spectator_betting_enabled=True,
            token_purchases_enabled=True,
            payouts_enabled=True,
            multi_camera_enabled=True,
        ))
        db.add(ArenaCapabilities(
            arena_id=arena_mumbai.id,
            wagering_enabled=False,
            token_purchases_enabled=True,
            multi_camera_enabled=True,
            message_if_disabled="Wagering not available in this region.",
        ))

        # Games
        racing = Game(
            game_code="robot_racing",
            title="Robot Racing",
            description="FPV robot racing. First to finish wins.",
            status=GameStatus.active,
            team_size_min=1,
            team_size_max=1,
            supports_tournaments=True,
            supports_wagering=True,
            default_duration_seconds=600,
        )
        football = Game(
            game_code="robot_football",
            title="Robot Football",
            description="Overhead camera football.",
            status=GameStatus.active,
            team_size_min=1,
            team_size_max=2,
            supports_tournaments=True,
            supports_wagering=True,
            default_duration_seconds=360,
        )
        db.add_all([racing, football])
        db.flush()

        db.add_all([
            GameVariant(game_id=racing.id, variant_code="1v1", title="1v1 Race", capacity=2),
            GameVariant(game_id=football.id, variant_code="1v1", title="1v1 Football", capacity=2),
            GameVariant(game_id=football.id, variant_code="2v2", title="2v2 Football", capacity=4),
        ])

        db.commit()
        print("Seed complete.")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()