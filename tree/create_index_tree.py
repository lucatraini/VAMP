from flask import Flask, render_template, request, jsonify, json
from elasticsearch import Elasticsearch
import numpy as np
import pandas as pd
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import math
import itertools
import operator
from collections import Counter
from numpy import var,std,mean
import matplotlib
from sklearn.cluster import MeanShift

def add_nodes(nodes, parent, child):
        if parent not in nodes:
            nodes[parent] = Node(parent)  
        if child not in nodes:
            nodes[child] = Node(child)
        nodes[child].parent = nodes[parent]



def create_path_dict(df):
    lista=[]
    service=[]
    nodes = {} 

    for parent, child in zip(df["parentId"],df["spanID"]):
        add_nodes(nodes, parent, child)

    
    path={}
    roots = list(df[~df["parentId"].isin(df["spanID"])]["parentId"].unique())
    for root in roots:
        for pre, _, node in RenderTree(nodes[root]):
                stringa=''
                lista_id=[]
                for i in node.ancestors:
                    if i.name is not np.nan:
                        stringa=stringa+'/'+df['name'][df['spanID']==i.name].item()
                        lista_id.append(df['spanID'][df['spanID']==i.name].item())
                        path[node.name] = {}
                        path[node.name].update({'path':stringa,
                                                    'service':df['name'][df['spanID']==node.name].item(),
                                                    'occ':[],'duration':df['duration'][df['spanID']==node.name].item()})
                        lista.append(stringa)
                        service.append(df['name'][df['spanID']==node.name].item())
                            
        
    for i in range(0,len(lista)):
        lista[i]=lista[i]+'/'+service[i]

    for i in path.keys():
        path[i]['path']=path[i]['path']+'/'+path[i]['service']
        path[i]['occ'].append(lista.count(path[i]['path']))

    #print(path)
    return path


def create_tree_from_paths(paths, delimiter="/"):
    print(paths)
    root = {"name": ""}
    for path in paths:
        segments = path['name'].split(delimiter)
        current_node = root
        for segment in segments:
            print(segment)
            # Find the child node with the given name, or create a new one
            child_node = next((child for child in current_node.get("children", []) if child["name"] == segment), None)
            if child_node is None:
                child_node = {"name": segment, "children": [],'duration':0,'var':0}
                current_node.setdefault("children", []).append(child_node)
                for child in current_node.get("children", []):
                    if child['name']==segment:
                        child['occ']=path['occ']
                        child['var']=(std(path['occ']))/(abs(mean(path['occ'])))
                        child['duration']=path['duration']
                        if child['var']>1:
                            child['var']=1
                        child['fill']=matplotlib.colors.to_hex([ 1, 1-child['var'], 1-child['var'] ])
                        
                        x=child['occ']
                        # inizializza l'algoritmo di clustering MeanShift con il parametro bandwidth
                        # il parametro bandwidth regola la sensibilità dell'algoritmo nella definizione dei cluster
                        ms = MeanShift(bandwidth=2)

                        # addestra l'algoritmo sulla lista di input
                        ms.fit([[i] for i in x])

                        # ottiene le etichette di cluster assegnate ad ogni elemento della lista di input
                        labels = ms.labels_

                        # ottiene i centri dei cluster identificati dall'algoritmo
                        cluster_centers = ms.cluster_centers_

                        # converte i centri dei cluster in interi
                        cluster_centers = [int(c[0]) for c in cluster_centers]

                        # crea un dizionario che conta il numero di elementi in ciascun cluster
                        cluster_counts = {}
                        for l in labels:
                            if l in cluster_counts:
                                cluster_counts[l] += 1
                            else:
                                cluster_counts[l] = 1

                        # calcola la percentuale di elementi in ciascun cluster
                        n_total = len(x)
                        child['perc_occ'] = {f"{c}-{c+2}": cluster_counts[i]/n_total*100 for i,c in enumerate(cluster_centers)}
                                                
            current_node = child_node
        #current_node["_value"] = paths[path]['occ']  # set value to None to indicate leaf node
    return root["children"]

'''
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
'''

#correct
def build_tree(paths,tree_dict):
    root = {'name': '', 'fill':'','children': {}}
    for path in paths:
        for tree in path['documents']:
            path_parts = tree['path'].strip('/').split('/')
            current_node = root
            for part in path_parts:
                if part not in current_node['children']:
                    current_node['children'][part] = {'name': part, 'duration': 0,'occ':[],'var':0, 'fill':'','children': {}}
                current_node = current_node['children'][part]
            current_node['fill']=tree_dict[tree['path']]['fill']
    root['name'] = 'root'
    return [root_to_list(root)]

def root_to_list(node):
    result = {'name': node['name'], 'fill':node['fill'], 'children': []}
    for child in node['children'].values():
        result['children'].append(root_to_list(child))
    return result
