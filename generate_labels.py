import json
import copy

with open("bookmarked_tweets.json","r") as f:
    d = json.load(f)

output_file_name = "labeled_tweets.json"

with open(output_file_name,"r") as f:
    labeled_tweets = json.load(f)

existing_ids = [tweet.get('id') for tweet in labeled_tweets]



for index, tweet in enumerate(d):
    print("\n\n\n")
    print(f"Labeling tweet {index+1} of {len(d)}.")
    print(tweet)
    if tweet.get('id') in existing_ids:
        continue
    clickbait_score = input("Please input a 0, 1, or 2, or 3(0=not clickbait, 1=sorta clickbait, 2=definitely clickbait, 3=not sure):")
    labeled_tweet = copy.deepcopy(tweet)
    labeled_tweet["score"] = clickbait_score
    labeled_tweets.append(labeled_tweet)
    with open("labeled_tweets.json", "w") as f:
        json.dump(labeled_tweets, f, indent=2)


