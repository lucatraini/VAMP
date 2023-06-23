from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch
import pandas as pd
import pymongo


es = Elasticsearch("http://localhost:9200",timeout=5000)

# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

# Create a collection
collection = db["latency"]

result = scan(es,index='jaeger-span-*', query={
        "query":{
            "bool": {
            "must": [
                {"match": {"kind":"SERVER"}},
                {
                "script": {
                "script": {
                    "source": "doc['traceID.keyword'].value == doc['spanID.keyword'].value"

                        }
                        } 
                    }]
                }
            }})
trace_id=[]

result = list(result)
size = len(result)
count = 0
for trace in result:
    print(f"Processing trace {count} of {size}")
    data={
            'traceId':trace['_source']['traceId'],
            'timestamp':trace['_source']['timestamp'],
            'latency':trace['_source']['duration'],
            'service':trace['_source']['name']}
        
    result=collection.insert_one(data)
    count+=1