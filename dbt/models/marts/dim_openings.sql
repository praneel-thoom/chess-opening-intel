with opening_counts as (
    select
        opening_eco,
        opening_name,
        opening_family,
        count(*) as name_frequency
    from {{ ref('stg_games') }}
    where opening_eco is not null
    group by opening_eco, opening_name, opening_family
),

ranked as (
    select
        *,
        row_number() over (
            partition by opening_eco
            order by name_frequency desc
        ) as rn
    from opening_counts
)

select
    opening_eco,
    opening_name,
    opening_family
from ranked
where rn = 1
