#!/usr/bin/env python
# coding: utf-8

# In[65]:


import os
import json


# In[66]:


all_headlines = dict()


# In[71]:


for event_dir in os.listdir():
    # Extract Event JSON file
    if os.path.isdir(event_dir) and event_dir[:9] == 'USAevents':
        fp = open('{}/step3_subevent_clustering/events.json'.format(event_dir), 'r')
        events = json.load(fp)
        fp.close()

        #Get all headlines for each event
        eventHeadlines = dict()
        for i in events['events'].keys():
            event = events['events'][i]['mainEvent']['eventArticles']
            headlines = []
            for article in event.keys():
                title = event[article]['cleanedTitle']
                if title != '':
                    headlines.append(title)
            eventHeadlines[i] = headlines

        all_headlines[event_dir] = eventHeadlines


# In[72]:


fp = open('headlines.json', 'w')
json.dump(all_headlines, fp)

