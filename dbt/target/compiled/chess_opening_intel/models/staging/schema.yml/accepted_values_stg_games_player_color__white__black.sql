
    
    

with all_values as (

    select
        player_color as value_field,
        count(*) as n_records

    from "postgres"."analytics_staging"."stg_games"
    group by player_color

)

select *
from all_values
where value_field not in (
    'white','black'
)


