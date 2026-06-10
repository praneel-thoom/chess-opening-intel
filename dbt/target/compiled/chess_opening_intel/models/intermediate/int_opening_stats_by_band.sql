select
    opening_eco,
    opening_name,
    opening_family,
    player_elo_band,
    time_control,
    count(*) as total_games,
    sum(points_scored) as total_points,
    round(avg(points_scored)::numeric, 4) as win_rate,
    sum(case when result = 'win' then 1 else 0 end) as wins,
    sum(case when result = 'draw' then 1 else 0 end) as draws,
    sum(case when result = 'loss' then 1 else 0 end) as losses,
    round(avg(num_moves)::numeric, 1) as avg_game_length
from "postgres"."analytics_intermediate"."int_games_enriched"
group by 1, 2, 3, 4, 5
having count(*) >= 50