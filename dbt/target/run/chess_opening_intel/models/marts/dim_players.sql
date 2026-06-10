
  
    

  create  table "postgres"."analytics_marts"."dim_players__dbt_tmp"
  
  
    as
  
  (
    select
    player_id,
    username,
    elo_rating,
    elo_band
from "postgres"."analytics_staging"."stg_players"
  );
  