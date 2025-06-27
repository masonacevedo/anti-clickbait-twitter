import os
import tweepy

# --- Step 1: Get your Client ID and Client Secret ---
# Make sure to set these as environment variables
client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")
print(os.environ.get("OAUTHLIB_INSECURE_TRANSPORT"))

if not client_id or not client_secret:
    raise Exception(
        "TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET environment variables must be set."
    )

# --- Step 2: Set up OAuth 2.0 User Handler ---
# The redirect_uri must match exactly what you have in your Twitter App settings.
# Scopes determine what permissions your app is requesting.
oauth2_handler = tweepy.OAuth2UserHandler(
    client_id=client_id,
    redirect_uri="http://localhost:8080/callback",  # Or "http://127.0.0.1:3000"
    scope=["tweet.read", "users.read", "timeline.read"],
    client_secret=client_secret,
)

# --- Step 3: Get the Authorization URL ---
authorization_url = oauth2_handler.get_authorization_url()
print(f"Please go here and authorize:\n{authorization_url}")

# --- Step 4: Get the user to paste the redirected URL ---
redirect_response = input("Paste the full redirect URL here: ")

# --- Step 5: Fetch the access token ---
# This exchanges the authorization code for an access token
oauth2_handler.fetch_token(redirect_response)

# --- Step 6: Create the Tweepy Client with the user's token ---
client = tweepy.Client(oauth2_handler)

# --- Step 7: Fetch the home timeline ---
# The get_home_timeline method automatically uses the authenticated user's context
response = client.get_home_timeline(max_results=10)

# --- Step 8: Print the tweets ---
if response.data:
    for tweet in response.data:
        print(f"ID: {tweet.id} - Text: {tweet.text}")
else:
    print("Could not find any tweets on your timeline.")

# common_words = ["the", "a", "I", "to", "and", "is", "in"]

# response = client.search_recent_tweets(query="mason lang:en")

# for e in response.data:
#     print(e)
#     print("mason\n\n\n")
