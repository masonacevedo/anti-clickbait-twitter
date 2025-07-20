import time
import os
from pipes import quote
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import tweepy
import json

OUTPUT_FILE_NAME = "bookmarked_tweets_v5.json"

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

def fetch_bookmarked_tweets(client, pagination_token=None, batch_size=100):
    return client.get_bookmarks(
        max_results=batch_size,
        expansions=["attachments.media_keys", "referenced_tweets.id"],
        media_fields=["url", "type", "preview_image_url"],
        tweet_fields=["card_uri", "text"],
        pagination_token=pagination_token
    )


def get_quoted_data(quoted_tweet, client):
    """This is currently broken, maybe?"""
    quoted_tweet_id = quoted_tweet.get('id')
    quoted_tweet = client.get_tweet(id=quoted_tweet_id, expansions=["attachments.media_keys"], media_fields=["url","type","preview_image_url"])
    print("sleeping for 30 seconds")
    time.sleep(30)
    quoted_text = quoted_tweet.data.text
    quoted_images = get_image_urls(quoted_tweet.data, quoted_tweet.includes)

    return quoted_text, quoted_images

def get_image_urls(t, includes_var):
    if t.attachments is None:
        return []

    urls = []
    media_keys = t.attachments.get('media_keys')
    for item in includes_var.get('media', []):
        if item.media_key in media_keys:
            if item.preview_image_url:
                urls.append(item.preview_image_url)
            if item.url:
                urls.append(item.url)
    return urls

def save_tweet(t, includes_var, client, tweets_so_far):
    base_text = t.text

    # get_image_urls should take in a tweet object and an includes var
    base_image_urls = get_image_urls(t, includes_var)
    
    if t.referenced_tweets and len(t.referenced_tweets) > 1:
        raise Exception(f"More than one tweet referenced: {t.referenced_tweets}")

    if t.referenced_tweets:
        quoted_tweet = t.referenced_tweets[0]
        # quoted_text, quoted_images = get_quoted_data(quoted_tweet, client)
    else:
        quoted_tweet = None

    

    new_tweet = {
        "id": t.id,
        "text": base_text,
        "images:": base_image_urls,
        **({"quoted_tweet": {
            "id": quoted_tweet.id
        }} if quoted_tweet else {})
    }

    tweets_so_far.append(new_tweet)
    with open(OUTPUT_FILE_NAME, "w") as f:
        json.dump(tweets_so_far, f, indent=2)



    


def main(client):
    bookmarked_tweets = fetch_bookmarked_tweets(client)
    print("Number of bookmarked tweets:", len(bookmarked_tweets.data))
    print("sleeping for 10 seconds")
    time.sleep(10)

    with open(OUTPUT_FILE_NAME, "r") as f:
        tweets_so_far = json.load(f)
    
    already_saved_ids = [tweet.get('id') for tweet in tweets_so_far]

    for index, tweet in enumerate(bookmarked_tweets.data):
        print(index)
        if not(tweet.id in already_saved_ids):
            save_tweet(tweet, bookmarked_tweets.includes, client, tweets_so_far)
    

    
def get_quoted_tweets(client):
    with open(OUTPUT_FILE_NAME, "r") as f:
        tweets_so_far = json.load(f)

    quoted_tweet_ids = []
    for tweet in tweets_so_far:
        if "quoted_tweet" in tweet:
            if "id" in tweet.get('quoted_tweet'):
                quoted_tweet_ids.append(tweet.get('quoted_tweet').get('id'))

    if len(quoted_tweet_ids) == 0:
        quoted_tweets = []
    else:
        quoted_tweets = client.get_tweets(ids=quoted_tweet_ids, expansions=["attachments.media_keys"], media_fields=["url","type","preview_image_url"])
    print("sleeping for 10 seconds")
    time.sleep(10)
    return quoted_tweets

def replace_ids_with_info(client):
    with open(OUTPUT_FILE_NAME, "r") as f:
        all_tweets = json.load(f)
    new_tweets = []
    
    quoted_tweets_response = get_quoted_tweets(client)

    if quoted_tweets_response == []:
        quoted_tweets = []
        quoted_tweets_includes = {}
    else:
        quoted_tweets = quoted_tweets_response.data
        quoted_tweets_includes = quoted_tweets_response.includes

    for tweet in all_tweets:
        if "quoted_tweet" in tweet:
            if "id" in tweet.get('quoted_tweet'):
                quoted_tweet = list(filter(lambda q: q.id == tweet.get('quoted_tweet').get('id'), quoted_tweets))[0]
                image_urls = get_image_urls(quoted_tweet, quoted_tweets_includes)

                tweet["quoted_tweet"] = {"text": quoted_tweet.text, "images": image_urls}

        new_tweets.append(tweet)

    with open(OUTPUT_FILE_NAME, "w") as f:
        json.dump(new_tweets, f, indent=2)


if __name__ == "__main__":
    client = get_twitter_client()
    main(client)
    replace_ids_with_info(client)
