select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        result as value_field,
        count(*) as n_records

    from "postgres"."analytics_staging"."stg_games"
    group by result

)

select *
from all_values
where value_field not in (
    'win','loss','draw'
)



      
    ) dbt_internal_test