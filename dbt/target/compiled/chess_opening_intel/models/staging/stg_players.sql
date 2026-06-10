select
    lower(player_id) as player_id,
    lower(username) as username,
    elo_rating::integer as elo_rating,
    time_control_pref,
    ingested_at,
    case
        when elo_rating between 400 and 999 then 'beginner'
        when elo_rating between 1000 and 1299 then 'intermediate'
        when elo_rating between 1300 and 1599 then 'club'
        when elo_rating between 1600 and 1999 then 'advanced'
        else 'expert'
    end as elo_band
from raw.players
where player_id is not null