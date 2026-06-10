select
    o.opening_eco,
    o.opening_name,
    o.opening_family,
    s.player_elo_band,
    s.time_control,
    s.total_games,
    s.win_rate,
    s.wins,
    s.draws,
    s.losses,
    s.avg_game_length,
    rank() over (
        partition by s.player_elo_band, s.time_control
        order by s.win_rate desc
    ) as win_rate_rank
from {{ ref('int_opening_stats_by_band') }} s
left join {{ ref('dim_openings') }} o
    on s.opening_eco = o.opening_eco
