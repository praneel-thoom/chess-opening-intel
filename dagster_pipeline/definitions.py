from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets import raw_games, raw_players
from .dbt_assets import chess_opening_dbt_assets
from .project import chess_dbt_project
from .schedules import weekly_refresh_schedule

defs = Definitions(
    assets=[raw_players, raw_games, chess_opening_dbt_assets],
    schedules=[weekly_refresh_schedule],
    resources={
        "dbt": DbtCliResource(project_dir=chess_dbt_project),
    },
)
