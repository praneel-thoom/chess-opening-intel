from pathlib import Path

from dagster_dbt import DbtProject

REPO_ROOT = Path(__file__).parent.parent

# Points Dagster at the existing dbt project rather than a copy of it.
# profiles.yml already reads its connection details from env vars
# (SUPABASE_DB_HOST, etc.), so no changes are needed there.
chess_dbt_project = DbtProject(
    project_dir=REPO_ROOT / "dbt",
    profiles_dir=REPO_ROOT / "dbt",
)

# Generates/refreshes manifest.json on `dagster dev` so asset metadata
# (column names, descriptions, lineage) stays in sync with the dbt models.
# In production this is skipped and the manifest is built once during
# deploy instead, via `dbt parse` or `dbt compile` in the image build step.
chess_dbt_project.prepare_if_dev()
