from kafka import KafkaProducer
import json
import time
import tweepy


ckey = ""
csecret = ""
atoken = ""
asecret = ""

# Twitter Authentication and Initialization
twitter_auth = tweepy.OAuthHandler(ckey, csecret)
twitter_auth.set_access_token(atoken, asecret)

twitter_api = tweepy.API(twitter_auth, wait_on_rate_limit_notify=True, retry_count=3, retry_delay=5)

print("######### Twitter Authentication Success ######")


producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))

# Twitter Stream Listener Implementation
class StreamListener(tweepy.StreamListener):
    count = 0

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            if tweet['coordinates'] is not None:
                tweetText = tweet["text"]
                user_name = tweet["user"]["name"]
                screen_name = tweet["user"]["screen_name"]
                coordinates = tweet["coordinates"]["coordinates"]



                tweet_struct = {
                    "coordinates": [coordinates[1], coordinates[0]],
                    "username": user_name,
                    "screenname": screen_name,
                    "text": tweetText,
                    "sentiment": "",
                    "id": tweet["id"],
                }
                print(tweet_struct)

                # Slow down the stream by sleeping for 10 seconds after every 10 tweets received
                self.count += 1
                if self.count == 10:
                    self.count = 0
                    print("Sleeping")
                    time.sleep(10)


                producer.send('tweet', json.dumps(tweet_struct))

        except (KeyError, UnicodeDecodeError, Exception) as e:
            pass

    def on_error(self, status_code):
        if status_code == 420:
            print("Rate Limit")
            return True


def main():
    print("Twitter Stream Begin!!")
    stream_listener = StreamListener()
    while True:
        try:
            streamer = tweepy.Stream(twitter_api.auth, listener=stream_listener)
            streamer.filter(track=['trump'],locations=[-180, -90, 180, 90], languages=['en'])
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()