from django.shortcuts import render
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
from elasticsearch import Elasticsearch
from requests_aws4auth import AWS4Auth
import elasticsearch
import time
import geocoder
from django.views.decorators.csrf import csrf_protect,csrf_exempt
import urllib3
from queue import Queue
from django.http import HttpResponse

# Create your views here.

flag = False
tweetQueue = Queue(maxsize=10)

host = ''
awsauth = AWS4Auth("", "", 'us-west-2', 'es')


es = elasticsearch.Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=elasticsearch.connection.RequestsHttpConnection
)

# es = Elasticsearch()

def index(request):

    return render(request,"home.html",{})


@csrf_protect
def home(request):
    # import twitter keys and tokens
    ckey = "lRpnCx9V3uT1k5haiOjgsMymg"
    csecret = "GAVMJfzMf7lKcR3sUg70qDIdeccjyGJ5giFEUGdLBq3YtvKHt4"
    atoken = "99720772-TiTD2K9Rv19Bid8Xm8My34GACinStkURjbMifzEEA"
    asecret = "FBk6JORnaJ9vNnudanqg6fMAjktEK4UNbwKKQO6BVTSbl"

    # create instance of elasticsearch
    # es = Elasticsearch([{'host': 'localhost', 'port': 9200}])



    query = str(request.POST.get('myword'))
    pass_list=list()



    res = es.search(size=5000, index="tweets", doc_type="twitter", body={
        "query": {
            "match": {
                "text": query
            }
        }
    })

    for j in res['hits']['hits']:
        pass_list.append(j['_source'])







    pass_list_final = json.dumps(pass_list)
    return render(request,"index.html",{"my_data": json.dumps(res),"query":query})

@csrf_exempt
def notifications(request):


    body = json.loads(request.body.decode("utf-8"))
    print(type(body))
    hdr = body['Type']

    if hdr == 'SubscriptionConfirmation':
        url = body['SubscribeURL']
        print("Subscription Confirmation - Visiting URL : " + url)
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        print(r.status)

    if hdr == 'Notification':
        print("SNS Notification")
        tweet = json.loads(body['Message'])
        es.index(index='tweets', doc_type='twitter', body=tweet)

        if not tweetQueue.full() and flag == False:
            tweetQueue.put(tweet)
            print("Tweet in queue")

    return HttpResponse(status=200)













