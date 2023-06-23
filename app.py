from flask import Flask, render_template, request, jsonify, json
from elasticsearch import Elasticsearch
import numpy as np
from numpy import var,std,mean
import pandas as pd
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import math
import itertools
import operator
from collections import Counter
from tree.reduce_tree import reduce_tree
from tree.path import create_path_dict,add_nodes
from tree.create_tree import get_children,get_nodes
from tree.create_index_tree import create_tree_from_paths
from sklearn.cluster import MeanShift, estimate_bandwidth,KMeans
from sklearn.metrics import silhouette_score
from elasticsearch.helpers import scan
from tree.create_index_tree import build_tree,root_to_list
import matplotlib
import pymongo
import urllib.parse
from scipy.spatial.distance import jensenshannon
from scipy.stats import median_abs_deviation, tmean, tstd
from scipy.special import kl_div


app = Flask(__name__)

es = Elasticsearch('http://localhost:9200',timeout=5000)

@app.route("/", methods=["GET"])
def tree():
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["latency"]
    # Collect unique names
    names = collection.distinct("service")

    with open("static/dataset_index.json") as f:
        dataset_index = json.load(f)
        for i, di in enumerate(dataset_index):
            di['id'] = i
    
        print(names)

    return render_template("tree.html",data=names,dataset=dataset_index)

@app.route("/latency", methods=["POST","GET"])
def tree_latency():
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["latency"]
    # Collect unique names
    names = collection.distinct("service")

    print(names)

    return render_template("latency_tree.html",data=names)

@app.route('/get_bins/<name>/<start>/<end>', methods=["GET","POST"])
def get_data(name,start,end):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    
    duration=[]
    # Create a collection
    collection = db["latency"]

    # Find documents that match a specific property
    query = { "service": name , "timestamp": {"$gte": int(start),"$lte":int(end)}  }

    results = collection.find(query)

    for result in results:
        duration.append(result['latency'])

    #print(duration)
    # Creating histogram   
    perc=np.percentile(duration,99)
    duration=[d for d in duration if d<perc]
    hist, bins = np.histogram(duration,bins=200)

    l = [{'key': int(bins[i]), 'value': float(hist[i])} for i in range(len(hist))]

    return json.dumps(l)

@app.route('/getTrace/<name>/<x0>/<x1>/<start>/<end>', methods=["GET","POST"])
def getTrace(name,x0,x1,start,end):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db['latency']

    query = {
        "service": name,
        "$and": [
        {"latency": {"$gte": int(x0)}},
        {"latency": {"$lte": int(x1)}}
    ],
    "timestamp": {"$gte": int(start),"$lte":int(end)}
    
    }

    result = collection.find(query)

    selected_group = []

    for document in result:
        selected_group.append(document['traceId'])    
    
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name,"traceId": { '$nin': selected_group },"timestamp": {"$gte": int(start),"$lte":int(end)}} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query, allowDiskUse=True)

    # Print the matching documents
    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'occ':[]}
                if len(trace_id)>0:
                    tree_dict[path['path']]['occ']=([0]*len(trace_id))
                    tree_dict[path['path']]['occ'].append(path['occ'])
                else: 
                    tree_dict[path['path']]['occ'].append(path['occ'])
            else: tree_dict[path['path']]['occ'].append(path['occ'])       
        trace_id.append(result['_id'])

    for occ in tree_dict.values():
        while len(occ['occ'])<len(trace_id):
            occ['occ'].append(0)


    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name,"traceId": { '$in': selected_group },"timestamp": {"$gte": int(start),"$lte":int(end)}} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query,  allowDiskUse=True)

    # Print the matching documents
    paths_selected=[]
    tree_dict_selected={}
    trace_id_selected=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict_selected:
                tree_dict_selected[path['path']]={'occ':[]}
                if len(trace_id_selected)>0:
                    tree_dict_selected[path['path']]['occ']=([0]*len(trace_id_selected))
                    tree_dict_selected[path['path']]['occ'].append(path['occ'])
                else: 
                    tree_dict_selected[path['path']]['occ'].append(path['occ'])
            else: tree_dict_selected[path['path']]['occ'].append(path['occ'])       
        trace_id_selected.append(result['_id'])

    for occ in tree_dict_selected.values():
        while len(occ['occ'])<len(trace_id_selected):
            occ['occ'].append(0)

    print(tree_dict_selected)


    merged_dict = {}
    epsilon = 1e-9
    for key in tree_dict.keys() | tree_dict_selected.keys():
        occ1 = tree_dict.get(key, {'occ': []})['occ']
        occ2 = tree_dict_selected.get(key, {'occ': []})['occ']
        max_length = max(len(occ1), len(occ2))
        occ1_padded = np.pad(occ1, (0, max_length - len(occ1)), mode='constant').tolist()
        occ2_padded = np.pad(occ2, (0, max_length - len(occ2)), mode='constant').tolist()
        # add epsilon to probabilities to avoid zeros
        occ1_padded = [p + epsilon for p in occ1_padded]
        occ2_padded = [p + epsilon for p in occ2_padded]
        
        # normalize the lists to be probability distributions
        p_sum = sum(occ1_padded)
        p_dist = np.array(occ1_padded) / p_sum

        q_sum = sum(occ2_padded)
        q_dist = np.array(occ2_padded) / q_sum
        # compute the KLD between the two lists
        kld = kl_divergence(occ1, occ2)
        print(kld)
        merged_dict[key] = {'var': kld}

    print(merged_dict)

    for path in merged_dict:
        if merged_dict[path]['var']>1:
            merged_dict[path]['var']=1
        merged_dict[path].update({'fill':matplotlib.colors.to_hex([ 1, 1-merged_dict[path]['var'], 1-merged_dict[path]['var'] ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        merged_dict[path].update({'service':parts[len(parts)-1]})

    print(merged_dict)

    tree = build_tree(paths,merged_dict)
    print(json.dumps(tree[0]))


    print("RESULT")
    print(result)
    return json.dumps(tree[0])


@app.route('/getTreeData/<name>', methods=["GET","POST"])
def getTreeData(name):
    
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query, allowDiskUse=True)

    # Print the matching documents
    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'occ':[]}
                if len(trace_id)>0:
                    tree_dict[path['path']]['occ']=([0]*len(trace_id))
                    tree_dict[path['path']]['occ'].append(path['occ'])
                else: 
                    tree_dict[path['path']]['occ'].append(path['occ'])
            else: tree_dict[path['path']]['occ'].append(path['occ'])       
        trace_id.append(result['_id'])

    for occ in tree_dict.values():
        while len(occ['occ'])<len(trace_id):
            occ['occ'].append(0)

    for path in tree_dict:
        tree_dict[path].update({'var':(std(tree_dict[path]['occ']))/(abs(mean(tree_dict[path]['occ'])))})
        if tree_dict[path]['var']>1:
            tree_dict[path]['var']=1
        tree_dict[path].update({'fill':matplotlib.colors.to_hex([ 1, 1-tree_dict[path]['var'], 1-tree_dict[path]['var'] ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        tree_dict[path].update({'service':parts[len(parts)-1]})

    
    
    tree = build_tree(paths,tree_dict)
    return(json.dumps(tree[0]))
    


@app.route('/getData_fromTimestamp/<name>/<start>/<end>', methods=["GET","POST"])
def get_fromTimestamp(name,start,end):
    print(name)
    print(type(int(start)))
    print(end)
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]
    
    query = {"service":{"$regex":name},"timestamp": {"$gte": int(start), "$lte": int(end)}}
    
    # define the aggregation pipeline
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$traceId", "documents": {"$push": "$$ROOT"}}}
    ]
    
    results = collection.aggregate(pipeline, allowDiskUse=True)

    # Print the matching documents
    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'occ':[]}
                if len(trace_id)>0:
                    tree_dict[path['path']]['occ']=([0]*len(trace_id))
                    tree_dict[path['path']]['occ'].append(path['occ'])
                else: 
                    tree_dict[path['path']]['occ'].append(path['occ'])
            else: tree_dict[path['path']]['occ'].append(path['occ'])       
        trace_id.append(result['_id'])

    for occ in tree_dict.values():
        while len(occ['occ'])<len(trace_id):
            occ['occ'].append(0)

    for path in tree_dict:
        tree_dict[path].update({'var':(std(tree_dict[path]['occ']))/(abs(mean(tree_dict[path]['occ'])))})
        if tree_dict[path]['var']>1:
            tree_dict[path]['var']=1
        tree_dict[path].update({'fill':matplotlib.colors.to_hex([ 1, 1-tree_dict[path]['var'], 1-tree_dict[path]['var'] ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        tree_dict[path].update({'service':parts[len(parts)-1]})

    tree = build_tree(paths,tree_dict)
    return(json.dumps(tree[0]))

@app.route('/getLatencyData_fromTimestamp/<name>/<start>/<end>', methods=["GET","POST"])
def getLatency_fromTimestamp(name,start,end):
    print(name)
    print(type(int(start)))
    print(end)
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]
    
    query = {"service":{"$regex":name},"timestamp": {"$gte": int(start), "$lte": int(end)}}
    
    # define the aggregation pipeline
    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$traceId", "documents": {"$push": "$$ROOT"}}}
    ]
    
    results = collection.aggregate(pipeline, allowDiskUse=True)

    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'latency':[]}
                tree_dict[path['path']]['latency'].append(np.median(path['latency']))
            else: tree_dict[path['path']]['latency'].append(np.median(path['latency']))

    for path in tree_dict:
        limit = np.percentile(tree_dict[path]['latency'],99)
        tree_dict[path].update({'var':(tstd(tree_dict[path]['latency'], limits=(0,limit)))/(tmean(tree_dict[path]['latency'],limits=(0,limit)))})
        if tree_dict[path]['var']>1:
            tree_dict[path]['var']=1
        tree_dict[path].update({'fill':matplotlib.colors.to_hex([ 1, 1-tree_dict[path]['var'], 1-tree_dict[path]['var'] ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        tree_dict[path].update({'service':parts[len(parts)-1]})

    print(tree_dict)
    tree = build_tree(paths,tree_dict)
    return(json.dumps(tree[0]))

@app.route('/getPercOcc', methods=["GET","POST"])
def getPercOcc():
    
    path = request.args.get('string')
    start_date = request.args.get('number')
    end_date = request.args.get('number1')
    print("START")
    print(start_date )
    #decoded_string = urllib.parse.unquote(string)
    #print("decoded:"+decoded_string)

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["latency"]

    print(path)
    print(path[:-1])
    # Find documents that match a specific property
    query = {"service": path.split("/")[0],"timestamp": {"$gte": int(start_date),"$lte":int(end_date)}}


    results = collection.find(query)

    trace_id=[trace['traceId'] for trace in results]

    # Create a collection
    collection = db["paths"]
    
    # Find documents that match a specific property
    query = {"path": path[:-1], "timestamp": {"$gte": int(start_date),"$lte":int(end_date)}}


    results = collection.find(query)

    occ=[]
    for trace in results:
        if trace['traceId'] in trace_id:
            occ.append(trace['occ'])
        else:
            occ.append(0)

    n_occ=np.unique(occ)
    print(len(n_occ))

    perc_occ={}
    X = np.array(list(zip(occ,np.zeros(len(occ)))), dtype=int)
    ms = KMeans(n_clusters=len(n_occ))
    ms.fit(X)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    for k in range(n_clusters_):
        my_members = labels == k
        perc_occ[str(np.unique(X[my_members,0]))]= int((len(X[my_members,0])/len(occ))*100)
    
    return perc_occ

@app.route('/get_binsSub', methods=["GET","POST"])
def get_data2():
    path = request.args.get('string')
    x = request.args.get('number')
    start = request.args.get('number1')
    end = request.args.get('number2')

    x=x.replace('[','')
    x=x.replace(']','')
    print(x)
    print(path[:-1])
    print(type(int(x)))

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Retreive latency data
    collection = db["latency"]
    query = { "service": path.split("/")[0], "timestamp": {"$gte": int(start),"$lte":int(end)} }
    results = collection.find(query)
    
    # Transform data to series 
    traceid_list = []
    latency_list = []
    for result in results:
        traceid_list.append(result['traceId'])
        latency_list.append(result['latency'])
    latency_series = pd.Series(latency_list, index=traceid_list)

    collection = db["paths"]

    if int(x)==0:
        # retrieve all traceid associated with the path
        results = collection.find({"timestamp": {"$gte": int(start),"$lte":int(end)},"$and": [{"service":path.split("/")[0]}, {"path": path[:-1]}]})
        traceid_list_ = [r['traceId'] for r in results if r['traceId'] not in latency_series.index]

    else:
        # traceid associated with occ=x for the path
        results = collection.find({"timestamp": {"$gte": int(start),"$lte":int(end)},"$and": [{"service":path.split("/")[0]}, {"path": path[:-1]}], "occ": int(x)})
        traceid_list_ = [r['traceId'] for r in results]

    selected_latency = latency_series[traceid_list_]


    # Creating histogram   
    perc=np.percentile(latency_series,99)
    latency_series=[d for d in latency_series if d<perc]

    #print(duration_link)
    hist, bins = np.histogram(latency_series,bins=200)

    # Find the corresponding bin indices
    bin_indices = np.digitize(selected_latency, bins)

    # Construct the histogram dictionary 
    hist_dict2 = [{'key': int(bins[i]), 'value': 0} for i in range(len(hist))]
    for i in range(len(bin_indices)):
        if bin_indices[i] > 0 and bin_indices[i] <= len(hist):
            hist_dict2[bin_indices[i]-1]['value'] += 1
    return json.dumps(hist_dict2)

@app.route('/get_bins_subgroup', methods=["GET","POST"])
def get_data_subgroup():
    path = request.args.get('string')
    x = request.args.get('number')
    
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    duration=[]
    # Create a collection
    collection = db["latency"]

    # Find documents that match a specific property
    query = { "service": path.split("/")[0] }

    results = collection.find(query)

    for result in results:
        duration.append(result['latency'])

    #print(duration)
    # Creating histogram   
    perc=np.percentile(duration,99)
    duration=[d for d in duration if d<perc]
    hist, bins = np.histogram(duration,bins=200)

    l = [{'key': int(bins[i]), 'value': float(hist[i])} for i in range(len(hist))]

    return json.dumps(l)

#tree for latency
@app.route('/compareLatency/<name>', methods=["GET","POST"])
def compareLatency(name):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query, allowDiskUse=True)

    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'latency':[]}
                tree_dict[path['path']]['latency'].append(np.median(path['latency']))
            else: tree_dict[path['path']]['latency'].append(np.median(path['latency']))

    for path in tree_dict:
        tree_dict[path].update({'var':(std(tree_dict[path]['latency']))/(abs(mean(tree_dict[path]['latency'])))})
        if tree_dict[path]['var']>1:
            tree_dict[path]['var']=1
        tree_dict[path].update({'fill':matplotlib.colors.to_hex([ 1-tree_dict[path]['var'], 0.8, 0  ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        tree_dict[path].update({'service':parts[len(parts)-1]})

    print(tree_dict)
    tree = build_tree(paths,tree_dict)
    return(json.dumps(tree[0]))

@app.route('/getPercDuration', methods=["GET","POST"])
def getPercDuration():
    
    path = request.args.get('string')

    start_date = request.args.get('number')
    end_date = request.args.get('number1')

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["latency"]

    print(path)
    print(path[:-1])
    # Find documents that match a specific property
    query = {"service": path.split("/")[0],"timestamp": {"$gte": int(start_date),"$lte":int(end_date)}}


    results = collection.find(query)

    trace_id=[trace['traceId'] for trace in results]

    # Create a collection
    collection = db["paths"]
    
    # Find documents that match a specific property
    query = {"path": path[:-1], "timestamp": {"$gte": int(start_date),"$lte":int(end_date)}}


    results = collection.find(query)

    duration=[]
    for trace in results:
        if trace['traceId'] in trace_id:
            duration.append(np.median(trace['latency']))
        else:
            duration.append(0)
    

    #n_occ=np.unique(occ)
    #print(len(n_occ))
    
    X = np.array(list(zip(duration,np.zeros(len(duration)))), dtype=int)
    sc = 0
    model = None
    for k in range(2,6):
        kmeans = KMeans(n_clusters=k, n_init='auto')
        kmeans.fit(X)
        sc_ = silhouette_score(X,kmeans.labels_) 
        if sc_ > sc:
            model = kmeans
            sc = sc_
    
    perc_duration={}
    if model is None:
        min_ = min(duration)
        max_ = max(duration)
        perc_duration[f'[{min_}-{max_}]'] = 100
    else:
        labels = model.labels_
        labels_unique = np.unique(labels)
        for label in labels_unique:
            mask = (labels == label)
            min_ = X[mask,0].min().item()
            max_ = X[mask,0].max().item()
            cluster_size = len(X[mask,0])
            if cluster_size > 0:
                range_ = f'[{min_}-{max_}]'
                perc_duration[range_]= round(cluster_size/len(duration)*100, 2)

    print(labels_unique)
    print(perc_duration)


    print('sorted')
    print(sorted(perc_duration))
    key_to_delete=[]
    for key,value in perc_duration.items():
        
        if value==0:
            key_to_delete.append(key)
    
    for key in key_to_delete:
        del perc_duration[key]
    
    return perc_duration

@app.route('/get_binsByLatency', methods=["GET","POST"])
def get_binsByLatency():
    path = request.args.get('string')
    x = request.args.get('string2')
    start = request.args.get('number1')
    end = request.args.get('number2')

    x=x.replace('[','')
    x=x.replace(']','')
    x=x.split("-")
    print(type(x[0]))
    print(x[1])
    print(path)
    print(path[:-1])
    #print(type(int(x)))

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Retreive latency data
    collection = db["latency"]
    query = { "service": path.split("/")[0], "timestamp": {"$gte": int(start),"$lte":int(end)} }
    results = collection.find(query)
    
    # Transform data to series 
    traceid_list = []
    latency_list = []
    for result in results:
        traceid_list.append(result['traceId'])
        latency_list.append(result['latency'])
    latency_series = pd.Series(latency_list, index=traceid_list)

    collection = db["paths"]

    if int(x[0])==0:
        # retrieve all traceid associated with the path
        results = collection.find({"timestamp": {"$gte": int(start),"$lte":int(end)},"$and": [{"service":path.split("/")[0]}, {"path": path[:-1]}]})
        traceid_list_ = [r['traceId'] for r in results if r['traceId'] not in latency_series.index]

    else:
        # traceid associated with occ=x for the path
        results = collection.find({"timestamp": {"$gte": int(start),"$lte":int(end)},
                                    "$and": [{"service":path.split("/")[0]}, {"path": path[:-1]}], 
                                    "latency": {"$gte": int(x[0]),"$lte":int(x[1])}})
        traceid_list_ = [r['traceId'] for r in results]

    selected_latency = latency_series[traceid_list_]


    # Creating histogram   
    perc=np.percentile(latency_series,99)
    latency_series=[d for d in latency_series if d<perc]

    #print(duration_link)
    hist, bins = np.histogram(latency_series,bins=200)

    # Find the corresponding bin indices
    bin_indices = np.digitize(selected_latency, bins)

    # Construct the histogram dictionary 
    hist_dict2 = [{'key': int(bins[i]), 'value': 0} for i in range(len(hist))]
    for i in range(len(bin_indices)):
        if bin_indices[i] > 0 and bin_indices[i] <= len(hist):
            hist_dict2[bin_indices[i]-1]['value'] += 1

    return json.dumps(hist_dict2)


@app.route('/compareGroupsLatency/<name>/<x0>/<x1>/<start>/<end>', methods=["GET","POST"])
def compareGroupsLatency(name,x0,x1,start,end):
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db['latency']

    query = {
        "service": name,
        "$and": [
        {"latency": {"$gte": int(x0)}},
        {"latency": {"$lte": int(x1)}}
    ],
    "timestamp": {"$gte": int(start),"$lte":int(end)}
    
    }

    result = collection.find(query)

    selected_group = []

    for document in result:
        selected_group.append(document['traceId'])


    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name,"traceId": { '$nin': selected_group },"timestamp": {"$gte": int(start),"$lte":int(end)}} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query, allowDiskUse=True)

    # Print the matching documents
    paths=[]
    tree_dict={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict:
                tree_dict[path['path']]={'latency':[]}
                tree_dict[path['path']]['latency'].append(np.median(path['latency']))
            else: tree_dict[path['path']]['latency'].append(np.median(path['latency']))


    # Find documents that match a specific property
    query = [
        # Match the documents possible
        { "$match": { "service": name,"traceId": { '$in': selected_group },"timestamp": {"$gte": int(start),"$lte":int(end)}} },

        # Group the documents and "count" via $sum on the values
        {
            '$group': {
                '_id': '$traceId',
                'documents': {'$push': '$$ROOT'}
            }
        }
    ]

    results = collection.aggregate(query, allowDiskUse=True)

    paths=[]
    tree_dict_selected={}
    trace_id=[]
    for result in results:
        paths.append(result)
        for path in result['documents']:
            #print(tree[path]['path'])
            if path['path'] not in tree_dict_selected:
                tree_dict_selected[path['path']]={'latency':[]}
                tree_dict_selected[path['path']]['latency'].append(np.median(path['latency']))
            else: tree_dict_selected[path['path']]['latency'].append(np.median(path['latency']))

    print(tree_dict_selected)

    merged_dict = {}
    epsilon = 1e-9
    for key in tree_dict.keys() | tree_dict_selected.keys():
        occ1 = tree_dict.get(key, {'latency': []})['latency']
        occ2 = tree_dict_selected.get(key, {'latency': []})['latency']
        num_bins = 100

        kl_divergence = compute_kl_divergence(occ1, occ2, num_bins)
        print(kl_divergence)
        merged_dict[key] = {'var': kl_divergence}

    print(merged_dict)

    for path in merged_dict:
        if merged_dict[path]['var']>1:
            merged_dict[path]['var']=1
        merged_dict[path].update({'fill':matplotlib.colors.to_hex([ 1, 1-merged_dict[path]['var'], 1-merged_dict[path]['var'] ])})
        parts = path.strip('/').split('/')
        print(parts[len(parts)-1])
        merged_dict[path].update({'service':parts[len(parts)-1]})

    print(merged_dict)

    tree = build_tree(paths,merged_dict)
    return json.dumps(tree[0])


@app.route('/getDiff', methods=["GET","POST"])
def getDiff():
    x0 = int(request.args.get("num1"));
    x1 = int(request.args.get("num2"));
    start=int(request.args.get("start"));
    end=int(request.args.get("end"));
    path = request.args.get('string')
    name=path.split("/")[0]
    print(name)
    print(path)
    print(x0)
    print(x1)

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db['latency']

    query = {
        "service": name,
        "$and": [
        {"latency": {"$gte": int(x0)}},
        {"latency": {"$lte": int(x1)}}
    ],
    "timestamp": {"$gte": int(start),"$lte":int(end)}
    
    }

    result = collection.find(query)

    selected_group = []

    for document in result:
        selected_group.append(document['traceId'])
    
    print(selected_group)
    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = {"traceId": { '$nin': selected_group },"path":path[:-1],"timestamp": {"$gte": int(start),"$lte":int(end)}} 
    results = collection.find(query)

    # Print the matching documents
    occ1=[]
    for result in results:
        occ1.append(result['occ'])


    # Find documents that match a specific property
    query = {"traceId": { '$in': selected_group },"path":path[:-1],"timestamp": {"$gte": int(start),"$lte":int(end)}} 

    results = collection.find(query)

    # Print the matching documents
    occ2=[]
    for result in results:
        occ2.append(result['occ'])

    print(occ1)
    print(occ2)
    
    # Concatenate the two lists
    concatenated_list = occ1 + occ2
    
    # Get the unique values from the concatenated list
    unique_values = np.unique(concatenated_list)

    # Sort the unique values in ascending order
    unique_values.sort()

    # Define the bin edges based on the unique values
    bin_edges = np.concatenate((unique_values, [unique_values[-1] + 1]))

    # Compute the histogram of the concatenated list
    hist_concatenated, _ = np.histogram(concatenated_list, bins=bin_edges, density=False)
    
    # Compute the probabilities by normalizing the histograms
    prob_concatenated = (hist_concatenated + np.finfo(float).eps) / len(concatenated_list)
    prob_list1 = (np.histogram(occ1, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(occ1)
    prob_list2 = (np.histogram(occ2, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(occ2)

    data = {
        'binEdges': bin_edges.tolist(),
        'probList1': np.histogram(occ1, bins=bin_edges, density=False)[0].tolist(),
        'probList2': np.histogram(occ2, bins=bin_edges, density=False)[0].tolist()
    }
    return json.dumps(data)

@app.route('/getDiffLatency', methods=["GET","POST"])
def getDiffLatency():
    x0 = int(request.args.get("num1"));
    x1 = int(request.args.get("num2"));
    start = int(request.args.get("start"));
    end = int(request.args.get("end"));
    path = request.args.get('string')
    name=path.split("/")[0]
    print(name)
    print(path)
    print(x0)
    print(x1)

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collection = db['latency']

    query = {
        "service": name,
        "$and": [
        {"latency": {"$gte": int(x0)}},
        {"latency": {"$lte": int(x1)}}
    ],
    "timestamp": {"$gte": int(start),"$lte":int(end)}
    
    }

    result = collection.find(query)

    selected_group = []

    for document in result:
        selected_group.append(document['traceId'])

    # Connect to the MongoDB database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Create a collection
    collection = db["paths"]

    # Find documents that match a specific property
    query = {"traceId": { '$nin': selected_group },"path":path[:-1],"timestamp": {"$gte": int(start),"$lte":int(end)}} 
    results = collection.find(query)

    # Print the matching documents
    latency1=[]
    for result in results:
        latency1.extend(result['latency'])


    # Find documents that match a specific property
    query = {"traceId": { '$in': selected_group },"path":path[:-1],"timestamp": {"$gte": int(start),"$lte":int(end)}} 

    results = collection.find(query)

    # Print the matching documents
    latency2=[]
    for result in results:
        latency2.extend(result['latency'])

    print(latency1)
    print(latency2)
    merged_dict = {}
    epsilon = 1e-9
    

        
    # Concatenate the two lists
    concatenated_list = latency1 + latency2
    
    # Determine the range of values in the concatenated list
    min_value = min(concatenated_list)
    max_value = max(concatenated_list)

    # Calculate the number of bins using the square root choice
    num_bins = int(np.sqrt(len(concatenated_list)))
    
    # Define the bin edges based on the concatenated list
    bin_edges = np.linspace(min_value, np.percentile(concatenated_list, 99), num_bins + 1)
    
    # Compute the histogram of the concatenated list
    hist_concatenated, _ = np.histogram(concatenated_list, bins=bin_edges, density=False)
    
    # Compute the probabilities by normalizing the histograms
    prob_concatenated = (hist_concatenated + np.finfo(float).eps) / len(concatenated_list)
    prob_list1 = (np.histogram(latency1, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(latency1)
    prob_list2 = (np.histogram(latency2, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(latency2)

    data = {
        'binEdges': bin_edges.tolist(),
        'probList1': np.histogram(latency1, bins=bin_edges, density=False)[0].tolist(),
        'probList2': np.histogram(latency2, bins=bin_edges, density=False)[0].tolist()
    }
    return json.dumps(data)

from collections import Counter
import math

def kl_divergence(list_a, list_b):
    # Count the occurrences of each element in the lists
    counter_a = Counter(list_a)
    counter_b = Counter(list_b)

    # Calculate the total number of elements in each list
    n_a = len(list_a)
    n_b = len(list_b)

    # Calculate the probability distributions of the lists
    prob_a = {k: v/n_a for k, v in counter_a.items()}
    print("PROBABILITY")
    print(prob_a)
    prob_b = {k: v/n_b for k, v in counter_b.items()}

    # Get the common keys between the two dictionaries
    common_keys = set(prob_a.keys()) & set(prob_b.keys())

    # Calculate the average probability distribution
    avg_prob = {k: 0.5*(prob_a.get(k, 0) + prob_b.get(k, 0)) for k in set(prob_a.keys()) | set(prob_b.keys())}

    # Calculate the KL divergences
    kl_div_a = sum(prob_a[k] * math.log(prob_a[k]/avg_prob[k]) for k in common_keys)
    kl_div_b = sum(prob_b[k] * math.log(prob_b[k]/avg_prob[k]) for k in common_keys)

    # Calculate the Jensen-Shannon divergence
    jsd = 0.5 * (kl_div_a + kl_div_b)
    return jsd

def compute_kl_divergence(list1, list2, num_bins):
    # Concatenate the two lists
    concatenated_list = list1 + list2
    
    # Determine the range of values in the concatenated list
    min_value = min(concatenated_list)
    max_value = max(concatenated_list)
    
    # Define the bin edges based on the concatenated list
    bin_edges = np.linspace(min_value, max_value, num_bins + 1)
    
    # Compute the histogram of the concatenated list
    hist_concatenated, _ = np.histogram(concatenated_list, bins=bin_edges, density=False)
    
    # Compute the probabilities by normalizing the histograms
    prob_concatenated = (hist_concatenated + np.finfo(float).eps) / len(concatenated_list)
    prob_list1 = (np.histogram(list1, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(list1)
    prob_list2 = (np.histogram(list2, bins=bin_edges, density=False)[0] + np.finfo(float).eps) / len(list2)
    
    # Calculate the KL divergence
    kl_divergence = np.sum(prob_list1 * np.log(prob_list1 / prob_concatenated)) + np.sum(prob_list2 * np.log(prob_list2 / prob_concatenated))
    
    return kl_divergence




