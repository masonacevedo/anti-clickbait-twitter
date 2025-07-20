import json
import copy


INPUT_FILE_NAME = "bookmarked_tweets_v5.json"
with open(INPUT_FILE_NAME,"r") as f:
    d = json.load(f)

OUTPUT_FILE_NAME = "labeled_tweets.json"
with open(OUTPUT_FILE_NAME,"r") as f:
    labeled_tweets = json.load(f)

existing_ids = [tweet.get('id') for tweet in labeled_tweets]



for index, tweet in enumerate(d):
    print("\n\n\n")
    print(f"Labeling tweet {index+1} of {len(d)}.")
    print(tweet)
    if tweet.get('id') in existing_ids:
        continue
    clickbait_score = input("Please input a 0, 1, or 2, or 3(0=not clickbait, 1=sorta clickbait, 2=definitely clickbait, 3=not sure):")
    if clickbait_score not in ["0", "1", "2", "3"]:
        raise Exception("Invalid score!!")
    labeled_tweet = copy.deepcopy(tweet)
    labeled_tweet["score"] = clickbait_score
    labeled_tweets.append(labeled_tweet)
    with open("labeled_tweets.json", "w") as f:
        json.dump(labeled_tweets, f, indent=2)


