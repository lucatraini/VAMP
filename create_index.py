from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch
import pandas as pd
from flask import Flask, render_template, request, jsonify, json
from elasticsearch import Elasticsearch
import numpy as np
from numpy import var,std,mean
import requests
import pandas as pd
from elasticsearch import Elasticsearch
import json
from datetime import datetime
from anytree import Node, RenderTree,LevelOrderGroupIter,AsciiStyle, PreOrderIter
import math
import itertools
import operator
from collections import Counter

from sklearn.cluster import MeanShift, estimate_bandwidth

# funzione ricorsiva per attraversare l'albero e creare la lista di path
def get_path(child_id, df):
    row = df[df['spanID'] == child_id]
    if row.empty:
        return ''
    parent_id = row.iloc[0]['parentId']
    name = row.iloc[0]['name']
    path = get_path(parent_id, df)
    if path:
        path += '/'
    paths[child_id]={}
    paths[child_id].update({'service':name})
    path += name
    paths[child_id].update({'path':path,'occ':[],'duration':df['duration'][df['spanID']==child_id].item()})
    return path

es = Elasticsearch("http://localhost:9200",timeout=5000)

es.indices.delete(index='tree',ignore=400)

# Define the settings to be applied
settings = {
    "index.mapping.total_fields.limit": 10000
}




index = es.indices.create(index="tree", body={
    "mappings": {
         "properties": {
            "ID":{"type":"text"},
            "timestamp":{"type":"duration"},
            "timestamp":{"type":"text"},
            "tree":{"type":"object",
            "enabled":False}
        }
    }
})

# Apply the settings to the index
es.indices.put_settings(index='tree', body={"settings": settings})

result = scan(es,index='jaeger-span-2022-05-19', query={
        "_source": ["traceId"],
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
for trace in list(result):
    trace_id.append(trace['_source']['traceId'])

i=0
for t in trace_id:
    print(len(trace_id))
    i=i+1
    print(i)
    trace=[]
    #i=i+1
    spans = scan(es,index='jaeger-span-2022-05-19', query={"query": {
        "match": {
            "traceId":t
            }
    }})


    for span in spans:
        trace.append(span['_source'])
    if len(trace)>1:
        df = pd.DataFrame(trace)
        paths={}
        # creazione della lista di path di nomi per ogni childId
        for child_id in df['spanID']:
            path = get_path(child_id, df)

        lista=[]
        for path in paths:
            lista.append(paths[path]['path'])
        print(paths)

        #numero di occorrenze di una path in una traccia
        for span in paths.keys():
            paths[span]['occ'].append(lista.count(paths[span]['path']))
        
       
        data={'ID':t,'service_name':df['name'][df['spanID']==t].item(),'duration':df['duration'][df['spanID']==t].item(),'timestamp':df['timestamp'][df['spanID']==t].item(),'tree':paths}
        res=es.index(
        index="tree",
        body=data
            )
    
