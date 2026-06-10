
    
    

with all_values as (

    select
        time_control as value_field,
        count(*) as n_records

    from "postgres"."analytics_staging"."stg_games"
    group by time_control

)

select *
from all_values
where value_field not in (
    'bullet','blitz'
)


