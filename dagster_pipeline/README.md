# Dagster pipeline

Replaces the GitHub Actions cron in `.github/workflows/pipeline.yml` with a
Dagster asset graph. Nothing about `ingestion/` or `dbt/` was rewritten;
Dagster just orchestrates the same scripts and the same dbt project.

## Assets

- `raw_players` — runs `ingestion/lichess_players.py` unchanged
- `raw_games` — runs `ingestion/lichess_games.py` unchanged, manual only
- `chess_opening_dbt_assets` — one asset per dbt model (`stg_games`,
  `int_opening_stats_by_band`, `fct_games`, `mart_opening_performance`, etc.),
  generated from the dbt manifest so the Dagster lineage graph matches the
  actual staging → intermediate → marts dependency chain instead of showing
  one opaque "run dbt" block.

## Schedule

`weekly_refresh_schedule` fires every Sunday at 6 AM UTC (same cron as
before) and materializes `raw_players` followed by the dbt assets.
`raw_games` is intentionally left out, same as the "Full game ingestion runs
manually" note in the main README.

## Local setup

```bash
pip install -r requirements.txt
# .env at the repo root needs the same vars pipeline.yml passed as secrets:
# SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER,
# SUPABASE_DB_PASSWORD, LICHESS_API_TOKEN
dagster dev
```

This opens the Dagster UI at `http://localhost:3000`, where you can inspect
the asset graph, materialize `raw_games` by hand, and see the schedule.

## Docker

`docker-compose.yml` builds a small image and runs `dagster dev` on port
3000, reading the same `.env` file. Bring it up with:

```bash
docker compose up --build
```

For anything beyond local/demo use, `dagster dev` is a single-process dev
server without a real scheduler daemon; a production deployment would split
this into a webserver + daemon + code-server via Dagster's `docker` or
`k8s` deployment examples, which is more than this project's cron-once-a-week
workload needs right now.

## Retiring GitHub Actions

Once this is running the way you want, delete or disable
`.github/workflows/pipeline.yml` so the job isn't triggered from two places.
