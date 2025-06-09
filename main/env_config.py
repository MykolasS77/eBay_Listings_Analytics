from dotenv import load_dotenv
import os

"""
    Gets information from the .env file, which is necessary for this program to function properly.
"""

load_dotenv()
EBAY_BROWSE_API = os.getenv("EBAY_BROWSE_API")
GET_TOKEN_LINK = os.getenv("EBAY_GENERATE_TOKEN")
SCOPE = os.getenv("EBAY_SCOPE")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
