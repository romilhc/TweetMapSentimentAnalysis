from multiprocessing.dummy import Pool as ThreadPool
import time
from kafka import KafkaConsumer
import boto3
from textblob import TextBlob
import json



sns = boto3.resource('sns',aws_access_key_id='',
    aws_secret_access_key='' )

topic = sns.Topic('')


def getkafkadata(n):

    consumer = KafkaConsumer('tweet',
                             bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('ascii')),
                             auto_offset_reset='earliest', enable_auto_commit=False)

    # code to retrieve all text data from Kafka Broker

    count = 0
    for message in consumer:
        try:
            #print(message)
            text = message.value
            text = json.loads(text)
            sentiment = TextBlob(text['text'])
            loc = text['coordinates']
            text['sentiment'] = sentiment.sentiment.polarity

            print(text)

            time.sleep(0.2)

            response = topic.publish(
                                    Message = json.dumps(text),
                                    MessageAttributes = {

                                    }
            )
            print(response)
            count += 1
        except Exception as e:
            print(e)


    return text


# function to be mapped over
def calculateParallel(numbers, threads):
    # configuring the worker pool

    pool = ThreadPool(threads)
    results = pool.map(getkafkadata,numbers)
    #print(results)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
    numbers = [1, 2, 3, 4, 5, 6]

    for n in range(50):
        tweet_text = calculateParallel(numbers, 10)
        #print "Tweet is ", tweet_text
        print(n)


