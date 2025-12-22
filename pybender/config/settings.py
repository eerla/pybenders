# pybenders/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1-mini"  # fast + cheap, perfect for batch
# MODEL = "gpt-5-nano"