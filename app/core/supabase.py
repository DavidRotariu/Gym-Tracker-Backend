import supabase
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
