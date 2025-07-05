import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import json
import requests
import time
import tweepy
import re
from bs4 import BeautifulSoup
import bs4

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
output_file_name = "bookmarked_tweets_v3.json"
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
                            media_type = "photo"
                        elif media.type == "video":
                            url = media.preview_image_url
                            media_type = "video_preview"
                        else:
                            url = None
                            media_type = None
                        if url and media_type:
                            try:
                                img_data = requests.get(url, timeout=10).content
                                ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
                                img_filename = f"tweet_{tweet.id}_{media_key}{ext}"
                                img_path = os.path.join(IMAGES_DIR, img_filename)
                                with open(img_path, "wb") as f:
                                    f.write(img_data)
                                tweet_info["media"].append({
                                    "path": img_path,
                                    "type": media_type
                                })
                            except Exception as e:
                                print(f"Failed to download image for tweet {tweet.id}: {e}")
            all_tweets.append(tweet_info)
            # If the tweet has a card_uri and no media, try to fetch a preview image from oEmbed
            if tweet_info["card_uri"] and not tweet_info["media"]:
                try:
                    # Extract the first URL from the tweet text
                    tweet_text = tweet_info["text"] or ""
                    if not isinstance(tweet_text, str):
                        tweet_text = str(tweet_text)
                    url_match = re.search(r'https?://\S+', tweet_text)
                    if url_match:
                        link_url = url_match.group(0)
                        page_resp = requests.get(link_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                        if page_resp.status_code == 200:
                            soup = BeautifulSoup(page_resp.text, "html.parser")
                            og_image = soup.find('meta', property='og:image')
                            # Ensure og_image is a Tag and has 'content'
                            og_image_url = None
                            if og_image and isinstance(og_image, bs4.element.Tag) and og_image.has_attr('content'):
                                og_image_url = og_image['content']
                            if og_image_url:
                                # Ensure og_image_url is a string
                                if not isinstance(og_image_url, str):
                                    og_image_url = str(og_image_url)
                                img_data = requests.get(og_image_url, timeout=10).content
                                ext = os.path.splitext(og_image_url)[1].split("?")[0]
                                if not ext:
                                    ext = ".jpg"
                                img_filename = f"tweet_{tweet.id}_card{ext}"
                                img_path = os.path.join(IMAGES_DIR, img_filename)
                                with open(img_path, "wb") as f:
                                    f.write(img_data)
                                if tweet_info["media"] is None:
                                    tweet_info["media"] = []
                                tweet_info["media"].append({
                                    "path": img_path,
                                    "type": "card_preview_og"
                                })
                except Exception as e:
                    print(f"Failed to fetch OG card preview image for tweet {tweet.id}: {e}")
            total_fetched += 1
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

print(f"Done! Saved {len(all_tweets)} tweets and their preview images (if any) to '{IMAGES_DIR}' and metadata to '{output_file_name}'.")
