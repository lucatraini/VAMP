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
import matplotlib

def get_nodes(node,links,df,tree_paths):
        print('NODE:',node)
        d = {}
        d['name'] = node
        #print(d)
        
        if node != 'Root':
            d['subname']=(df['service'].loc[df['spanID']==node]).item()
            
            if node in tree_paths:
                d['perc_occ']=[]
                ''' 
                if tree_paths[node]['var']>1:
                    tree_paths[node]['var']=1
                d['fill']=matplotlib.colors.to_hex([ 1, 1-tree_paths[node]['var'], 1-tree_paths[node]['var'] ])
                
                if tree_paths[node]['var']>1.0: 
                    d['fill']='#FF0000'
                elif node in tree_paths and tree_paths[node]['var']>0 and tree_paths[node]['var']<0.8:
                    d['fill']='#FFCCCC'
                else:
                    d['fill']='#d2d2d2'
                '''    
            #print(df.loc[df['spanID']==node].values)
            #d['operationName']=(df['operationName'].loc[df['spanID']==node]).item()
            if df['traceId'].loc[df['spanID']==node].item()== 'ac1ce7bff44eb64e':
                d['traceId']=(df['traceId'].loc[df['spanID']==node]).item()
        else: 
            d['fill']='#d2d2d2'

        if node == '1fc683eba00e56fb':
            d['subname']=(df['process'].loc[df['spanID']==node]).item()['serviceName']
        
        children = get_children(node,links)
        
        print(children)
        if children:
            d['children'] = [get_nodes(child,links,df,tree_paths) for child in children]
        return d

def get_children(node,links):
    return [x[1] for x in links if x[0] == node]