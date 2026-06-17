import pandas as pd
from ingestion.utils import get_engine

engine = get_engine()
df = pd.read_sql("SELECT * FROM analytics_marts.mart_opening_performance ORDER BY player_elo_band, win_rate DESC", engine)
df.to_csv("mart_opening_performance.csv", index=False)
print(f"Exported {len(df)} rows")