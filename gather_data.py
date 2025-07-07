import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import tweepy

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


def save_quoted_data(quoted_tweet):
    pass

def save_tweet(t):
    base_text = t.text
    quote_tweet = t.referenced_tweets
    print("base_text:", base_text)
    print("quote_tweet:", quote_tweet)

    if not(quote_tweet):
        quoted_text = None
        quoted_images = []
    else:
        save_quoted_data(quote_tweet)

    


def main():
    client = get_twitter_client()
    bookmarked_tweets = fetch_bookmarked_tweets(client)
    first_tweet = bookmarked_tweets.data[0]
    for tweet in bookmarked_tweets.data:
        save_tweet(tweet)
        print(tweet)
        print(dir(tweet))
        input()
    

    

if __name__ == "__main__":
    main()