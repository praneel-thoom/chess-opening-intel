select
    g.*,
    p.elo_band as player_elo_band,
    p.elo_rating as player_rating
from "postgres"."analytics_staging"."stg_games" g
join "postgres"."analytics_staging"."stg_players" p
    on g.player_id = p.player_id