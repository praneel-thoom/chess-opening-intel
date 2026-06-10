import time
import os
import requests
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    url = (
        f"postgresql://{os.getenv('SUPABASE_DB_USER')}:{os.getenv('SUPABASE_DB_PASSWORD')}"
        f"@{os.getenv('SUPABASE_DB_HOST')}:{os.getenv('SUPABASE_DB_PORT')}/{os.getenv('SUPABASE_DB_NAME')}"
    )
    return create_engine(url)

def get_lichess_headers():
    return {
        "Authorization": f"Bearer {os.getenv('LICHESS_API_TOKEN')}",
        "Accept": "application/x-ndjson"
    }

def rate_limited_get(url, headers=None, params=None, delay=1.5, stream=False):
    time.sleep(delay)
    response = requests.get(
        url,
        headers=headers or get_lichess_headers(),
        params=params,
        stream=stream
    )
    response.raise_for_status()
    return response