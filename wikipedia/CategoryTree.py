#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import numpy as np 


# In[2]:


class CategoryNode:
    def __init__(self, category):
        self.category = category
        self.children = []
        self.pages = []
        self.texts = []
        self.vector = None
        
    def add_child(self, node):
        self.children.append(node)
                
    def __str__(self):
        return self.category
    


# In[3]:


class CategoryTree:
    def __init__(self, vectorizer):
        self.root = CategoryNode("Root")
        self.corpus = []
        self.vectorizer = vectorizer
        
    def load_json(self, file):
        tree = json.load(open(file,'r'))
        tree = json.loads(tree)
        corpus = []
        print("Category Tree loading...")            

        for name in tree.keys():
            node = CategoryNode(name)
            self.root.add_child(node)
            node.pages = tree[name]['pages']
            node.texts = tree[name]['texts']
            corpus += node.texts
            node_children = set(tree[name]) - set(["pages","texts"])
            for name_1 in node_children:
                node_1 = CategoryNode(name_1)
                node.add_child(node_1)
                node_1.pages = tree[name][name_1]['pages']
                node_1.texts = tree[name][name_1]['texts']
                corpus += node_1.texts
                node_1_children = set(tree[name][name_1]) - set(["pages","texts"])
                for name_2 in node_1_children:
                    node_2 = CategoryNode(name_2)
                    node_1.add_child(node_2)
                    node_2.pages = tree[name][name_1][name_2]['pages']
                    node_2.texts = tree[name][name_1][name_2]['texts']
                    corpus += node_2.texts
        print("Vectorizer is fitting...")
        self.vectorizer.fit(corpus)
        
        del corpus
        del tree
        
        print("Transforming tree...")
        self.vectorize()
        
        print("Tree is ready!")
                    
    def vectorize(self):
        for node in self.root.children:
            try:
                node.vector = np.mean(self.vectorizer.transform(node.texts),axis=0)
            except ValueError:
                node.vector = np.zeros((1, 100000))
            for node_1 in node.children:
                try:
                    node_1.vector = np.mean(self.vectorizer.transform(node_1.texts),axis=0)
                except ValueError:
                    node_1.vector = np.zeros((1, 100000))
                for node_2 in node_1.children:
                    try:
                        node_2.vector = np.mean(self.vectorizer.transform(node_2.texts),axis=0)
                    except ValueError:
                        node_2.vector = np.zeros((1, 100000))
                        
    def search(self, words, similarity_metric):
        input_vector = self.vectorizer.transform(words)
        result = []
        maximum = 0, None
        for node in self.root.children:
            test = similarity_metric(node.vector,input_vector)[0][0]
            if test > maximum[0]:
                maximum = test, node
        result.append(maximum)
        
        maximum = 0, None
        for node in result[-1][1].children:
            test = similarity_metric(node.vector,input_vector)[0][0]
            if test > maximum[0]:
                maximum = test, node
        result.append(maximum)
        
        maximum = 0, None
        for node in result[-1][1].children:
            test = similarity_metric(node.vector,input_vector)[0][0]
            if test > maximum[0]:
                maximum = test, node
        result.append(maximum)
        
        return result
            


# In[4]:


tree = CategoryTree(TfidfVectorizer(stop_words=list(stopwords.words('english')),
                                    max_features=100000))
tree.load_json('search_tree_with_text.json')


# In[13]:


for i in tree.search([], cosine_similarity):
    print(i[1],"(similarity {})".format(i[0]))

