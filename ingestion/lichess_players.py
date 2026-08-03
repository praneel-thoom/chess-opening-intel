import pandas as pd
import ndjson
from datetime import datetime, timezone
from utils import get_engine, rate_limited_get

# ELO bands to sample from
ELO_BANDS = [
    {"label": "beginner",     "min": 600,  "max": 999},
    {"label": "intermediate", "min": 1000, "max": 1299},
    {"label": "club",         "min": 1300, "max": 1599},
    {"label": "advanced",     "min": 1600, "max": 1999},
    {"label": "expert",       "min": 2000, "max": 9999},
]

PERF_TYPES = ["bullet", "blitz"]
PLAYERS_PER_BAND = 200


def fetch_expert_players() -> list[dict]:
    """Fetch expert players from top leaderboards."""
    players = []
    seen_ids = set()

    for perf_type in PERF_TYPES:
        url = f"https://lichess.org/api/player/top/200/{perf_type}"
        response = rate_limited_get(url, headers={"Accept": "application/json"})
        data = response.json()

        for user in data.get("users", []):
            rating = user.get("perfs", {}).get(perf_type, {}).get("rating", 0)
            player_id = user["id"]

            if rating >= 2000 and player_id not in seen_ids:
                seen_ids.add(player_id)
                players.append({
                    "player_id": player_id,
                    "username": user["username"],
                    "elo_rating": rating,
                    "elo_band": "expert",
                    "time_control_pref": perf_type,
                    "ingested_at": datetime.now(timezone.utc)
                })

    return players[:PLAYERS_PER_BAND]


def fetch_players_by_rating_range(band: dict) -> list[dict]:
    """Fetch players from arena tournaments filtered by rating range."""
    players = []
    seen_ids = set()

    url = "https://lichess.org/api/tournament"
    response = rate_limited_get(url, headers={"Accept": "application/json"})
    tournaments = response.json()

    all_tournaments = (
        tournaments.get("created", []) +
        tournaments.get("started", []) +
        tournaments.get("finished", [])
    )

    for tournament in all_tournaments:
        if len(players) >= PLAYERS_PER_BAND:
            break

        tournament_id = tournament.get("id")
        if not tournament_id:
            continue

        results_url = f"https://lichess.org/api/tournament/{tournament_id}/results"
        try:
            results_response = rate_limited_get(results_url, stream=True)
            for line in results_response.iter_lines():
                if line:
                    try:
                        player = ndjson.loads(line.decode())[0]
                        rating = player.get("rating", 0)
                        player_id = player.get("username", "").lower()

                        if band["min"] <= rating <= band["max"] and player_id not in seen_ids:
                            seen_ids.add(player_id)
                            players.append({
                                "player_id": player_id,
                                "username": player.get("username"),
                                "elo_rating": rating,
                                "elo_band": band["label"],
                                "time_control_pref": "blitz",
                                "ingested_at": datetime.now(timezone.utc)
                            })
                    except Exception:
                        continue
        except Exception:
            continue

    return players[:PLAYERS_PER_BAND]


def save_players(players: list[dict]):
    if not players:
        print("No players to save.")
        return

    df = pd.DataFrame(players)
    df = df.drop_duplicates(subset=["player_id"])

    engine = get_engine()

    with engine.connect() as conn:
        existing = pd.read_sql("SELECT player_id FROM raw.players", conn)
    
    existing_ids = set(existing["player_id"])
    df = df[~df["player_id"].isin(existing_ids)]

    if df.empty:
        print("All players already exist. Nothing new to insert.")
        return

    df.to_sql(
        name="players",
        con=engine,
        schema="raw",
        if_exists="append",
        index=False
    )
    print(f"Saved {len(df)} new players.")


def main():
    all_players = []
    for band in ELO_BANDS:
        print(f"Fetching players for band: {band['label']}")
        if band["label"] == "expert":
            players = fetch_expert_players()
        else:
            players = fetch_players_by_rating_range(band)
        print(f"Found {len(players)} players in {band['label']} band")
        all_players.extend(players)

    save_players(all_players)
    print(f"Total players ingested: {len(all_players)}")


if __name__ == "__main__":
    main()