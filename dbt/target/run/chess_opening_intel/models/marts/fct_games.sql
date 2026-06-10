
  
    

  create  table "postgres"."analytics_marts"."fct_games__dbt_tmp"
  
  
    as
  
  (
    select * from "postgres"."analytics_intermediate"."int_games_enriched"
  );
  