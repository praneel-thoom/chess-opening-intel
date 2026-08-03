from dagster import AssetSelection, ScheduleDefinition, define_asset_job

from .assets import raw_players
from .dbt_assets import chess_opening_dbt_assets

# Same two steps pipeline.yml ran: refresh the player pool, then rebuild +
# test the dbt models. raw_games is deliberately excluded, same as today.
weekly_refresh_job = define_asset_job(
    name="weekly_refresh_job",
    selection=AssetSelection.assets(raw_players)
    | AssetSelection.assets(chess_opening_dbt_assets),
)

# Sunday 6 AM UTC, matching `cron: '0 6 * * 0'` in the old workflow.
weekly_refresh_schedule = ScheduleDefinition(
    job=weekly_refresh_job,
    cron_schedule="0 6 * * 0",
    execution_timezone="UTC",
)
