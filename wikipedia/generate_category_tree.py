#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import json
import mwparserfromhell as wp


# In[8]:


wiki_pages = json.load(open('files.json','r'))
wiki_pages = json.loads(wiki_pages)


# In[2]:


class CategoryNode:
    def __init__(self, category, parent):
        self.category = category
        self.parent = parent 
        self.children = []
        filename = category.replace(' ', '_').replace('&','_').replace('/','_')
        if category == 'Root':
            self.pages = None
            self.texts = None
        else:
            self.pages = self.add_pages(filename)
            self.texts = self.add_texts()
        
    def add_child(self, node):
        self.children.append(node)
        
    def add_pages(self, page):
        pages = []
        try:
            fp = open("category_files/"+page, 'r')
            for line in fp:
                if len(line) > 1:
                    pages.append(re.search('[0-9]+ (.*)', line).group(1))
            return pages    
        except FileNotFoundError:
            pass
            
        try:
            wiki_pages[self.category]
            pages.append(self.category)
        except KeyError:
            try:
                wiki_pages[self.category[:-1]]
                pages.append(self.category[:-1])
            except KeyError:
                words = self.category.split(' ')
                for word in words:
                    try:
                        word = word[0].upper() + word[1:]
                        wiki_pages[word]
                        pages.append(word)
                    except KeyError:
                        continue
        return pages
    
    def add_texts(self):
        self.texts = []
        for page in self.pages:
            try:
                fp = open(wiki_pages[page], 'r')
                text = fp.read()
                fp.close()
                parser = wp.parse(text)
                sections = parser.strip_code().split('\n')
                text = ""            
                for sec in sections:
                    if '.' in sec:
                        text += sec + ' '
                self.texts.append(text)
            except KeyError:
                continue
        
    def delete_child(self, cat):
        try:
            self.children.remove(cat)
        except ValueError:
            pass
        
    def __str__(self):
        return self.category


# In[3]:


fp = open("root_tree", "r")
level_one = None
level_two = None
root_node = CategoryNode("Root", None)
fp.readline()
nodes = set()
for line in fp:
    if '####' in line:
        continue
    first_split = line.split(' (')
    second_split = first_split[0].split(' [[:')
    hashs, cat = second_split[0], second_split[1].split('|')[0].split("Category:")[1]
    if hashs == "#":
        node = CategoryNode(cat, root_node)
        root_node.add_child(node)
        level_one = node
        if len(node.pages) == 0:
            root_node.delete_child(cat)
    elif hashs == "##":
        node = CategoryNode(cat, level_one)
        level_one.add_child(node)
        level_two = node
        if len(node.pages) == 0:
            level_one.delete_child(cat)
    else:
        node = CategoryNode(cat, level_two)
        level_two.add_child(node)
        if len(node.pages) == 0:
            level_two.delete_child(cat)


# In[16]:


copy = dict()
for node in root_node.children:
    copy[node.category] = dict()
    copy[node.category]['pages'] = node.pages
    copy[node.category]['texts'] = node.texts
    
    for node_1 in node.children:
        copy[node.category][node_1.category] = dict()
        copy[node.category][node_1.category]['pages'] = node_1.pages
        copy[node.category][node_1.category]['texts'] = node_1.texts

        for node_2 in node_1.children:
            copy[node.category][node_1.category][node_2.category] = dict()
            copy[node.category][node_1.category][node_2.category]['pages'] = node_2.pages
            copy[node.category][node_1.category][node_2.category]['texts'] = node_2.texts

fp = open('search_tree_with_text', 'w')           
json_str = json.dumps(copy)
json.dump(json_str, fp)

