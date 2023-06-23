from multiprocessing import Pool
from functools import partial

from elasticsearch.helpers import scan
from elasticsearch import Elasticsearch
import pandas as pd
import pymongo


# Connect to the MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

# Create a collection
collection = db["paths"]

# funzione ricorsiva per attraversare l'albero e creare la lista di path
def get_path(child_id, df):
    row = df[df['spanID'] == child_id]
    if row.empty:
        return None
    
    row = row.iloc[0]
    if row['traceId'] == row['spanID']:
        return row['name']
    
    if 'parentId' not in df.columns:
        return child_id
    
    parent_id = row['parentId']
    name = row['name']
    kind = row['kind']
    
    path = get_path(parent_id, df)
    if path is None:
        return None
    elif kind=='SERVER':
        path += '/' + name
    return path


def process_spans(traceid):   
    print(f"Processing trace {traceid}")
    es = Elasticsearch("http://localhost:9200",timeout=5000)

    trace=[]
    
    spans = scan(es,index='jaeger-span-*', query={"query": {
        "match": {
            "traceId": traceid
            }
    }})


    for span in spans:
        trace.append(span['_source'])
    
    if len(trace)>1:
        df = pd.DataFrame(trace)
        paths_list=[]
        
        spanid_list = df[df.kind=='SERVER']['spanID']
        # creazione della lista di path di nomi per ogni childId
        for child_id in spanid_list:
            path = get_path(child_id, df)
            if path is None:
                continue
            else:                       

                data={
                    'traceId':df['traceId'][df['spanID']==traceid].item(),
                    'timestamp':df['timestamp'][df['spanID']==traceid].item(),
                    'latency':[df['duration'][df['spanID']==child_id].item()],
                    'occ':1,
                    'path':path,
                    'service':df['name'][df['spanID']==traceid].item()}

                if not paths_list:
                    paths_list.append(data)
                else:
                    for dict_in_list in paths_list:
                        if dict_in_list['path'] == data['path']:
                            # Se lo troviamo, incrementiamo il valore di 'occ'
                            dict_in_list['occ'] += 1
                            dict_in_list['latency'].append(data['latency'][0])
                            break
                    else:
                        # Se non lo troviamo, aggiungiamo il nuovo dizionario alla lista
                        paths_list.append(data)

        result=collection.insert_many(paths_list)
            #print(paths_list)
    else:
        df = pd.DataFrame(trace) 

        data={
                'traceId':df['traceId'].item(),
                'timestamp':df['timestamp'].item(),
                'latency':[df['duration'].item()],
                'occ':1,
                'path':df['name'].item(),
                'service':df['name'].item()}
        
        result=collection.insert_one(data)
    
    es.close()

    return result


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200",timeout=5000)


    result = scan(es,index='jaeger-span-*', query={
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
                        }
                    ]
                    }
                }})
    
    trace_id_set = {doc['_source']['traceId']  for doc in result}

    print(f"TraceId loaded")

    already_processed =set(collection.distinct("traceId"))

    print(f"TraceId already processed loaded")

    trace_id_set -= already_processed

    es.close()


    with Pool(4) as pool:
        pool.map(process_spans, trace_id_set)




        