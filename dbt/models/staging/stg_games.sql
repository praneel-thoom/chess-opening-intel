select
    game_id,
    player_id,
    opponent_rating::integer as opponent_rating,
    lower(player_color) as player_color,
    lower(result) as result,
    upper(opening_eco) as opening_eco,
    opening_name,
    split_part(opening_name, ':', 1) as opening_family,
    lower(time_control) as time_control,
    game_date::date as game_date,
    num_moves::integer as num_moves,
    case
        when lower(result) = 'win' then 1.0
        when lower(result) = 'draw' then 0.5
        else 0.0
    end as points_scored,
    ingested_at
from raw.games
where game_id is not null
    and opening_eco is not null
    and num_moves >= 5
    and opponent_rating > 0
