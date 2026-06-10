
  
    

  create  table "postgres"."analytics_marts"."dim_openings__dbt_tmp"
  
  
    as
  
  (
    select distinct
    opening_eco,
    opening_name,
    opening_family
from "postgres"."analytics_staging"."stg_games"
where opening_eco is not null
  );
  