select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

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



      
    ) dbt_internal_test