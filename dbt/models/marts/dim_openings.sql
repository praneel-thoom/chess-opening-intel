select distinct
    opening_eco,
    opening_name,
    opening_family
from {{ ref('stg_games') }}
where opening_eco is not null
