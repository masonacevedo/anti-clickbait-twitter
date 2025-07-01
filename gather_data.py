import os
import json
import requests
import time
import tweepy

# --- Setup ---
client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")

if not client_id or not client_secret:
    raise Exception(
        "TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET environment variables must be set."
    )

oauth2_handler = tweepy.OAuth2UserHandler(
    client_id=client_id,
    redirect_uri="http://localhost:8080/callback",
    scope=["tweet.read", "users.read", "timeline.read", "bookmark.read"],
    client_secret=client_secret,
)

authorization_url = oauth2_handler.get_authorization_url()
print(f"Please go here and authorize:\n{authorization_url}")

redirect_response = input("Paste the full redirect URL here: ")

oauth2_handler.fetch_token(redirect_response)
access_token = oauth2_handler.access_token
refresh_token = oauth2_handler.refresh_token

client = tweepy.Client(access_token, consumer_key=client_id, consumer_secret=client_secret)

# --- Download setup ---
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Try to load the last pagination token if it exists
pagination_token = None
if os.path.exists("last_pagination_token.txt"):
    with open("last_pagination_token.txt", "r") as f:
        pagination_token = f.read().strip()
output_file_name = "bookmarked_tweets.json"
with open(output_file_name, "r") as f:
    all_tweets = json.load(f)

seen_ids = [tweet.get('id') for tweet in all_tweets]

pagination_token = None
total_fetched = 0
max_total = 1000  # Twitter API may limit to 800, but try 1000
BATCH_SIZE = 100

print("Fetching up to 1000 bookmarked tweets in batches of 100...")

while total_fetched < max_total:
    print('continuing from tippy top...')
    input('press enter to continue!')
    print("pagination token at beginning:", pagination_token)
    response = client.get_bookmarks(
        max_results=BATCH_SIZE,
        expansions=["attachments.media_keys"],
        media_fields=["url", "type", "preview_image_url"],
        tweet_fields=["card_uri", "text"],
        pagination_token=pagination_token
    )
    media_dict = {}
    if hasattr(response, "includes") and response.includes and "media" in response.includes:
        for media in response.includes["media"]:
            media_dict[media.media_key] = media

    if response.data:
        
        for tweet in response.data:
            print("continuing from inside...")
            if tweet.id in seen_ids:
                print("about to skip")
                continue
            tweet_info = {
                "id": tweet.id,
                "text": getattr(tweet, "text", None),
                "card_uri": getattr(tweet, "card_uri", None),
                "media": []
            }
            if hasattr(tweet, "attachments") and tweet.attachments and "media_keys" in tweet.attachments:
                for media_key in tweet.attachments["media_keys"]:
                    media = media_dict.get(media_key)
                    if media:
                        if media.type == "photo":
                            url = media.url
                        elif media.type == "video":
                            url = media.preview_image_url
                        else:
                            url = None
                        if url:
                            try:
                                img_data = requests.get(url, timeout=10).content
                                ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
                                img_filename = f"tweet_{tweet.id}_{media_key}{ext}"
                                img_path = os.path.join(IMAGES_DIR, img_filename)
                                with open(img_path, "wb") as f:
                                    f.write(img_data)
                                tweet_info["media"].append(img_path)
                            except Exception as e:
                                print(f"Failed to download image for tweet {tweet.id}: {e}")
            all_tweets.append(tweet_info)
        total_fetched += len(response.data)
        print(f"Fetched {total_fetched} tweets so far...")
    else:
        print("No more tweets found.")
        break

    print("Response meta:", response.meta)
    # Pagination
    pagination_token = response.meta.get('next_token') if hasattr(response, "meta") else None
    if not pagination_token:
        print("no pagination token found")
        break
    print("pagination token at end:", pagination_token)
    print("\n\n\n")
    time.sleep(3)  # Be nice to the API

# Save all tweet data
with open(output_file_name, "w") as f:
    json.dump(all_tweets, f, indent=2)

# Save the last pagination token for future use
if pagination_token:
    with open("last_pagination_token.txt", "w") as f:
        f.write(pagination_token)

print(f"Done! Saved {len(all_tweets)} tweets and their preview images (if any) to '{IMAGES_DIR}' and metadata to 'bookmarked_tweets.json'.")
