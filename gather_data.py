import os
from pipes import quote
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import tweepy
import pickle

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


def get_quoted_data(quoted_tweet):
    print(dir(quoted_tweet))
    print(quoted_tweet.data)
    print("items:", quoted_tweet.items())
    print("keys:", quoted_tweet.keys())
    print("values:", quoted_tweet.values())
    input()
    return None, None
    # pass

def save_tweet(t):
    base_text = t.text
    if t.referenced_tweets and len(t.referenced_tweets) > 1:
        raise Exception(f"More than one tweet referenced: {t.referenced_tweets}")

    if t.referenced_tweets:
        quoted_tweet = t.referenced_tweets[0]
        quoted_text, quoted_images = get_quoted_data(quoted_tweet)
    else:
        quoted_text = None
        quoted_images = []

    


def main():
    client = get_twitter_client()
    bookmarked_tweets = fetch_bookmarked_tweets(client)

    with open("foo.pkl", "wb") as f:
        pickle.dump(bookmarked_tweets.data, f)

    first_tweet = bookmarked_tweets.data[0]

    for tweet in bookmarked_tweets.data:
        save_tweet(tweet)
    

    

if __name__ == "__main__":
    main()