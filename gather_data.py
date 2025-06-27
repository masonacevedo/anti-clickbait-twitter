import os
from oauthlib.oauth2.rfc6749.grant_types import refresh_token
import tweepy

client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")
print(os.environ.get("OAUTHLIB_INSECURE_TRANSPORT"))

if not client_id or not client_secret:
    raise Exception(
        "TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET environment variables must be set."
    )

oauth2_handler = tweepy.OAuth2UserHandler(
    client_id=client_id,
    redirect_uri="http://localhost:8080/callback",  # Or "http://127.0.0.1:3000"
    scope=["tweet.read", "users.read", "timeline.read", "bookmark.read"],
    client_secret=client_secret,
)

authorization_url = oauth2_handler.get_authorization_url()
print(f"Please go here and authorize:\n{authorization_url}")

redirect_response = input("Paste the full redirect URL here: ")

oauth2_handler.fetch_token(redirect_response)
access_token = oauth2_handler.access_token
refresh_token = oauth2_handler.refresh_token

client = tweepy.Client(bearer_token=os.environ.get("TWITTER_BEARER_TOKEN"))
user_id = os.environ.get("MY_TWITTER_USER_ID")


response = client.get_bookmarks(user_id=user_id, max_results=10)

if response.data:
    for tweet in response.data:
        print(f"ID: {tweet.id} - Text: {tweet.text}")
else:
    print("Something went wrong.")
