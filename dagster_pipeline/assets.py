import sys
from pathlib import Path
from subprocess import run, PIPE

from dagster import AssetExecutionContext, MetadataValue, Output, asset

REPO_ROOT = Path(__file__).parent.parent
INGESTION_DIR = REPO_ROOT / "ingestion"


def _run_ingestion_script(context: AssetExecutionContext, script_name: str) -> str:
    """
    Runs one of the existing ingestion/*.py scripts as a subprocess, exactly
    as GitHub Actions did. Nothing about lichess_players.py or
    lichess_games.py needs to change for Dagster to orchestrate them; this
    just gives each script an asset identity, logs, and a place to attach
    run metadata.
    """
    result = run(
        [sys.executable, script_name],
        cwd=INGESTION_DIR,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
    )
    if result.stdout:
        context.log.info(result.stdout)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise Exception(f"{script_name} exited with code {result.returncode}:\n{result.stderr}")
    return result.stdout


@asset(
    group_name="ingestion",
    description=(
        "Refreshes the sampled player pool across all 5 ELO bands from "
        "Lichess leaderboards and arena tournaments. This is the piece that "
        "used to run alone on the weekly GitHub Actions cron."
    ),
)
def raw_players(context: AssetExecutionContext) -> Output[None]:
    output = _run_ingestion_script(context, "lichess_players.py")
    return Output(None, metadata={"stdout_tail": MetadataValue.text(output[-2000:])})


@asset(
    group_name="ingestion",
    description=(
        "Ingests up to 500 games per player for players not already in "
        "raw.games. Left out of the weekly schedule on purpose, matching "
        "the README's note that full game ingestion runs manually, since a "
        "full pass takes hours against the Lichess rate limit. Materialize "
        "this one by hand from the Dagster UI when you want fresh games."
    ),
    deps=[raw_players],
)
def raw_games(context: AssetExecutionContext) -> Output[None]:
    output = _run_ingestion_script(context, "lichess_games.py")
    return Output(None, metadata={"stdout_tail": MetadataValue.text(output[-2000:])})
