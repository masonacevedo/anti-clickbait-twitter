import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import json
import requests
import time
import tweepy
import re
from bs4 import BeautifulSoup
import bs4

# --- Helper Functions ---
def get_twitter_client():
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
    return client

def load_pagination_token(filename="last_pagination_token.txt"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    return None

def save_pagination_token(token, filename="last_pagination_token.txt"):
    if token:
        with open(filename, "w") as f:
            f.write(token)

def load_all_tweets(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_all_tweets(tweets, filename):
    with open(filename, "w") as f:
        json.dump(tweets, f, indent=2)

def extract_first_url(text):
    if not isinstance(text, str):
        text = str(text)
    url_match = re.search(r'https?://\S+', text)
    if url_match:
        return url_match.group(0)
    return None

def download_media(media, tweet_id, media_key, images_dir):
    if media.type == "photo":
        url = media.url
        media_type = "photo"
    elif media.type == "video":
        url = media.preview_image_url
        media_type = "video_preview"
    else:
        return None
    if url and media_type:
        try:
            img_data = requests.get(url, timeout=10).content
            ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
            img_filename = f"tweet_{tweet_id}_{media_key}{ext}"
            img_path = os.path.join(images_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(img_data)
            return {"path": img_path, "type": media_type}
        except Exception as e:
            print(f"Failed to download image for tweet {tweet_id}: {e}")
    return None

def fetch_og_image(url, tweet_id, images_dir):
    try:
        page_resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if page_resp.status_code == 200:
            soup = BeautifulSoup(page_resp.text, "html.parser")
            og_image = soup.find('meta', property='og:image')
            og_image_url = None
            if og_image and isinstance(og_image, bs4.element.Tag) and og_image.has_attr('content'):
                og_image_url = og_image['content']
            if og_image_url:
                if not isinstance(og_image_url, str):
                    og_image_url = str(og_image_url)
                img_data = requests.get(og_image_url, timeout=10).content
                ext = os.path.splitext(og_image_url)[1].split("?")[0]
                if not ext:
                    ext = ".jpg"
                img_filename = f"tweet_{tweet_id}_card{ext}"
                img_path = os.path.join(images_dir, img_filename)
                with open(img_path, "wb") as f:
                    f.write(img_data)
                return {"path": img_path, "type": "card_preview_og"}
    except Exception as e:
        print(f"Failed to fetch OG card preview image for tweet {tweet_id}: {e}")
    return None

def fetch_bookmarked_tweets(client, pagination_token, batch_size):
    return client.get_bookmarks(
        max_results=batch_size,
        expansions=["attachments.media_keys"],
        media_fields=["url", "type", "preview_image_url"],
        tweet_fields=["card_uri", "text"],
        pagination_token=pagination_token
    )

def process_tweet(tweet, media_dict, seen_ids, images_dir):
    if tweet.id in seen_ids:
        print("about to skip")
        return None
    tweet_info = {
        "id": tweet.id,
        "text": getattr(tweet, "text", None),
        "card_uri": getattr(tweet, "card_uri", None),
        "media": []
    }
    # Download media
    if hasattr(tweet, "attachments") and tweet.attachments and "media_keys" in tweet.attachments:
        for media_key in tweet.attachments["media_keys"]:
            media = media_dict.get(media_key)
            if media:
                media_info = download_media(media, tweet.id, media_key, images_dir)
                if media_info:
                    if not isinstance(tweet_info["media"], list):
                        tweet_info["media"] = []
                    tweet_info["media"].append(media_info)
    return tweet_info

def try_add_og_image(tweet_info, images_dir):
    if tweet_info["card_uri"] and not tweet_info["media"]:
        tweet_text = tweet_info["text"] or ""
        link_url = extract_first_url(tweet_text)
        if link_url:
            og_media = fetch_og_image(link_url, tweet_info["id"], images_dir)
            if og_media:
                if not isinstance(tweet_info["media"], list):
                    tweet_info["media"] = []
                tweet_info["media"].append(og_media)

# --- Main Script ---

def main():
    client = get_twitter_client()
    IMAGES_DIR = "images"
    os.makedirs(IMAGES_DIR, exist_ok=True)
    output_file_name = "bookmarked_tweets_v4.json"
    all_tweets = load_all_tweets(output_file_name)
    # Normalize: ensure all tweet['media'] is a list
    for tweet in all_tweets:
        if "media" not in tweet or not isinstance(tweet["media"], list):
            tweet["media"] = []
    seen_ids = [tweet.get('id') for tweet in all_tweets]
    pagination_token = load_pagination_token()
    total_fetched = 0
    max_total = 1000
    BATCH_SIZE = 100

    print("Fetching up to 1000 bookmarked tweets in batches of 100...")
    while total_fetched < max_total:
        print('continuing from tippy top...')
        input('press enter to continue!')
        print("pagination token at beginning:", pagination_token)
        response = fetch_bookmarked_tweets(client, pagination_token, BATCH_SIZE)
        media_dict = {}
        if hasattr(response, "includes") and response.includes and "media" in response.includes:
            for media in response.includes["media"]:
                media_dict[media.media_key] = media
        if response.data:
            for tweet in response.data:
                print("continuing from inside...")
                tweet_info = process_tweet(tweet, media_dict, seen_ids, IMAGES_DIR)
                if tweet_info is None:
                    continue
                try_add_og_image(tweet_info, IMAGES_DIR)
                all_tweets.append(tweet_info)
                total_fetched += 1
                print(f"Fetched {total_fetched} tweets so far...")
        else:
            print("No more tweets found.")
            break
        print("Response meta:", response.meta)
        pagination_token = response.meta.get('next_token') if hasattr(response, "meta") else None
        if not pagination_token:
            print("no pagination token found")
            break
        print("pagination token at end:", pagination_token)
        print("\n\n\n")
        time.sleep(3)

    save_all_tweets(all_tweets, output_file_name)
    save_pagination_token(pagination_token)
    print(f"Done! Saved {len(all_tweets)} tweets and their preview images (if any) to '{IMAGES_DIR}' and metadata to '{output_file_name}'.")

if __name__ == "__main__":
    main()
