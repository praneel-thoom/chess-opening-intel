from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

from .project import chess_dbt_project


@dbt_assets(manifest=chess_dbt_project.manifest_path)
def chess_opening_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    One Dagster asset per dbt model (stg_games, int_opening_stats_by_band,
    fct_games, mart_opening_performance, etc.), wired together using the
    actual staging -> intermediate -> marts dependency graph from the dbt
    manifest. This replaces the old two-step `dbt test` then `dbt run` in
    pipeline.yml (which tested models before they were rebuilt) with
    `dbt build`, which runs each model and tests it immediately after.
    """
    yield from dbt.cli(["build"], context=context).stream()
