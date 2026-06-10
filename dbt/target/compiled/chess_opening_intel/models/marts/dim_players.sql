select
    player_id,
    username,
    elo_rating,
    elo_band
from "postgres"."analytics_staging"."stg_players"