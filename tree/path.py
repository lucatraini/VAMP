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


def add_nodes(nodes, parent, child):
        if parent not in nodes:
            nodes[parent] = Node(parent)  
        if child not in nodes:
            nodes[child] = Node(child)
        nodes[child].parent = nodes[parent]



def create_path_dict(df,t):
    tree_path={}
    lista=[]
    service=[]
    nodes = {} 

    for parent, child in zip(df["parentId"],df["spanID"]):
        add_nodes(nodes, parent, child)

    tree_path={'ID':t,'root':df.loc[df['spanID']==t].to_dict('records')}
    path={}
    roots = list(df[~df["parentId"].isin(df["spanID"])]["parentId"].unique())
    for root in roots:
        for pre, _, node in RenderTree(nodes[root]):
                stringa=''
                lista_id=[]
                for i in node.ancestors:
                    if i.name != 0:
                        stringa=stringa+'/'+df['name'][df['spanID']==i.name].item()
                        lista_id.append(df['spanID'][df['spanID']==i.name].item())
                        path[node.name] = {}
                        path[node.name].update({'path':stringa,
                                             'parentId':df['parentId'][df['spanID']==node.name].item(),
                                             'traceId':df['traceId'][df['spanID']==node.name].item(),
                                             'spanID':df['spanID'][df['spanID']==node.name].item(),
                                             'duration':df['duration'][df['spanID']==node.name].item(),
                                             'service':df['name'][df['spanID']==node.name].item(),
                                             'occ':[]})
                        lista.append(stringa)
                        service.append(df['name'][df['spanID']==node.name].item())
        
    for i in range(0,len(lista)):
        lista[i]=lista[i]+'/'+service[i]

    
    for i in path.keys():
        path[i]['path']=path[i]['path']+'/'+path[i]['service']
    
    
    tree_path['tree']=path
    for i in tree_path['tree'].keys():
        tree_path['tree'][i]['occ'].append(lista.count(tree_path['tree'][i]['path']))

    print(tree_path)
    return tree_path