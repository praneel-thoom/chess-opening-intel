import pandas as pd
import ndjson
from datetime import datetime, timezone
from sqlalchemy import text
from utils import get_engine, rate_limited_get

MAX_GAMES_PER_PLAYER = 500

engine = get_engine()


def get_all_players() -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT player_id, username, elo_band FROM raw.players"))
        return [dict(row._mapping) for row in result]


def get_already_processed_players() -> set:
    """Get usernames already in raw.games to allow resuming."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DISTINCT player_id FROM raw.games"))
            return {row[0] for row in result}
    except Exception:
        return set()


def fetch_games_for_player(username: str, elo_band: str) -> list[dict]:
    url = f"https://lichess.org/api/games/user/{username}"
    params = {
        "max": MAX_GAMES_PER_PLAYER,
        "perfType": "bullet,blitz",
        "opening": "true",
        "clocks": "false",
        "evals": "false",
        "since": int((datetime.now(timezone.utc).replace(day=1)).timestamp() * 1000)
    }

    games = []
    try:
        response = rate_limited_get(url, params=params, stream=True)
        for line in response.iter_lines():
            if line:
                try:
                    game = ndjson.loads(line.decode())[0]

                    opening = game.get("opening", {})
                    opening_eco = opening.get("eco")
                    opening_name = opening.get("name")

                    if not opening_eco or not opening_name:
                        continue

                    players = game.get("players", {})
                    white = players.get("white", {})
                    black = players.get("black", {})

                    if white.get("user", {}).get("name", "").lower() == username.lower():
                        player_color = "white"
                        player_rating = white.get("rating", 0)
                        opponent_rating = black.get("rating", 0)
                    else:
                        player_color = "black"
                        player_rating = black.get("rating", 0)
                        opponent_rating = white.get("rating", 0)

                    winner = game.get("winner")
                    if winner is None:
                        result = "draw"
                    elif winner == player_color:
                        result = "win"
                    else:
                        result = "loss"

                    speed = game.get("speed", "")
                    if speed not in ["bullet", "blitz"]:
                        continue

                    games.append({
                        "game_id": game.get("id"),
                        "player_id": username.lower(),
                        "opponent_rating": opponent_rating,
                        "player_color": player_color,
                        "result": result,
                        "opening_eco": opening_eco,
                        "opening_name": opening_name,
                        "opening_family": opening_name.split(":")[0].strip(),
                        "time_control": speed,
                        "game_date": datetime.fromtimestamp(
                            game.get("createdAt", 0) / 1000, tz=timezone.utc
                        ).date(),
                        "num_moves": len(game.get("moves", "").split()),
                        "ingested_at": datetime.now(timezone.utc)
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"Error fetching games for {username}: {e}")

    return games


def save_games(games: list[dict]):
    if not games:
        return

    df = pd.DataFrame(games)
    df = df.drop_duplicates(subset=["game_id"])

    df.to_sql(
        name="games",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False
    )


def main():
    players = get_all_players()
    already_processed = get_already_processed_players()
    remaining = [p for p in players if p["player_id"] not in already_processed]

    print(f"Total players: {len(players)}")
    print(f"Already processed: {len(already_processed)}")
    print(f"Remaining: {len(remaining)}")

    total_games = 0
    for i, player in enumerate(remaining):
        username = player["username"]
        elo_band = player["elo_band"]

        games = fetch_games_for_player(username, elo_band)
        if games:
            save_games(games)
            total_games += len(games)

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(remaining)} players, {total_games} games this run.")

    print(f"Done. Total games ingested this run: {total_games}")


if __name__ == "__main__":
    main()