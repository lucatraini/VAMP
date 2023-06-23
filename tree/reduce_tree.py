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
from itertools import chain


def reduce_tree(tree_paths,df):
    # Python code to demonstrate 
    # finding duplicate values from dictionary
    
    
    # initialising dictionary
    ini_dict = {'a':1, 'b':2, 'c':3, 'd':2}
    
    # printing initial_dictionary
    #print("initial_dictionary", str(tree_paths))
    
    # finding duplicate values
    # from dictionary using set
    rev_dict = {}
    for key, value in tree_paths.items():
        rev_dict.setdefault(value['path'], set()).add(key)
    
    
    result = filter(lambda x: len(x)>1, rev_dict.values())


    for i in rev_dict.values():
        path_id=list(i)
        for j in range(1,len(path_id)):
            df.drop(df.loc[df['spanID']== path_id[j]].index, inplace=True)
            df.loc[df['parentId']== path_id[j],'parentId']=path_id[0]

    return df
