select
    player_id,
    username,
    elo_rating,
    elo_band
from {{ ref('stg_players') }}
