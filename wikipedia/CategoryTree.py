#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import numpy as np 


# In[2]:


MAX_FEATURES = 75000


# In[3]:


class CategoryNode:
    def __init__(self, category):
        self.category = category
        self.children = []
        self.pages = []
        self.texts = []
        self.vectors = []
        
    def add_child(self, node):
        self.children.append(node)
                
    def __str__(self):
        return self.category
    
    def delete_child(self, cat):
        del_index = None
        for i, child in enumerate(self.children):
            if child.category == cat:
                del_index = i 
                break
        del self.children[del_index]
        
    def infer_vector(self):
        vectors = []
        for child in self.children:
            try:
                if np.all((child.vectors != 0)):
                    if type(vectors) is list:
                        vectors = child.vectors
                    else:
                        vectors = np.append(vectors, child.vectors, axis = 0)
            except ValueError:
                continue
                
        if type(vectors) is not list:        
            self.vectors = np.mean(vectors, axis = 0).reshape((1, MAX_FEATURES))
        else:
            self.vectors = np.zeros((1, MAX_FEATURES))
        
    


# In[4]:


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
        
        unchecked_nodes = [(name, self.root, []) for name in tree.keys()]
        
        while len(unchecked_nodes) > 0:
            cat, parent_node, path = unchecked_nodes[0]
            unchecked_nodes = unchecked_nodes[1:]

            node = CategoryNode(cat)
            parent_node.add_child(node)

            section = tree
            for p in path:
                section = section[p]

            node.pages = section[cat]['pages']
            node.texts = section[cat]['texts']
            corpus += node.texts
            cat_children = set(section[cat]) - set(["pages","texts"])

            node_children = [(child, node, path + [cat]) for child in cat_children]
            unchecked_nodes += node_children
        
        
        print("Vectorizer is fitting...")
        self.vectorizer.fit(corpus)
        
        del corpus
        del tree
        
        print("Transforming tree...")
        self.vectorize()
        
        print("Tree is ready!")
        
    def load_vectorizer(self, vectorizer_filename, pages_filename):
        self.vectorizer = pickle.load(open(vectorizer_filename, 'rb'))

        tree = json.load(open(pages_filename,'r'))
        tree = json.loads(tree)
        print("Category Tree loading...")
        
        unchecked_nodes = [(name, self.root, []) for name in tree.keys()]
        
        while len(unchecked_nodes) > 0:
            cat, parent_node, path = unchecked_nodes[0]
            unchecked_nodes = unchecked_nodes[1:]

            node = CategoryNode(cat)
            parent_node.add_child(node)

            section = tree
            for p in path:
                section = section[p]

            node.pages = section[cat]['pages']
            node.texts = section[cat]['texts']
            cat_children = set(section[cat]) - set(["pages","texts"])

            node_children = [(child, node, path + [cat]) for child in cat_children]
            unchecked_nodes += node_children
        
        del tree
        
        print("Transforming tree...")
        self.vectorize()
        
        print("Tree is ready!")
    
    def save_vectorizer(self, vectorizer_filename):
        pickle.dump(self.vectorizer, open(vectorizer_filename, 'wb'))
        
    def vectorize(self):      
        bad_nodes = []
        unchecked_nodes = [child for child in self.root.children]
        while len(unchecked_nodes) != 0:
            node = unchecked_nodes[0]
            unchecked_nodes = unchecked_nodes[1:]
            try:
                node.vectors = self.vectorizer.transform(node.texts)
            except ValueError:
                node.vectors = np.zeros((1, MAX_FEATURES))
                bad_nodes.append(node)
                
            unchecked_nodes += node.children

        for node in bad_nodes:
            node.infer_vector()
        
                
    def search(self, words, similarity_metric, fingerprint=False):
        if not fingerprint:
            input_vector = self.vectorizer.transform(words)
        else:
            input_vector = np.array([0 if _ not in words.keys() else 1 for idx,_ in enumerate(self.vectorizer.get_feature_names())]).reshape([1,len(self.vectorizer.get_feature_names())])
        result = []
        current_node = self.root
        while len(current_node.children) != 0:
            cat_maximum = 0, None
            page_maximum = 0, None
            
            for node in current_node.children:
                cat_vec = np.mean(node.vectors, axis=0)
                if np.max(cat_vec) == 0:
                    continue
                test = similarity_metric(cat_vec, input_vector)[0][0]
                if test > cat_maximum[0]:
                    cat_maximum = test, node
                    
            for i, vec in enumerate(cat_maximum[1].vectors):
                test = similarity_metric(vec, input_vector)[0][0]
                if test > page_maximum[0]:
                    if len(cat_maximum[1].pages) != 0:
                        page_maximum = test, cat_maximum[1].pages[i]
                    else:
                        page_maximum = None
                        
            result.append(cat_maximum)
            result.append(page_maximum)
            
            current_node = cat_maximum[1]
        
        return result
            


# In[5]:


tree = CategoryTree(TfidfVectorizer(stop_words=list(stopwords.words('english')),
                                    max_features=MAX_FEATURES))
tree.load_json('search_tree_with_text.json')


# In[6]:


tree.save_vectorizer('vectorizer.pickle')


# In[7]:


tree = CategoryTree(None)
tree.load_vectorizer('vectorizer.pickle', 'search_tree_with_text.json')


# In[8]:


article_text = """
NASHVILLE, Tenn. (AP) — Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on records and on TV, died Friday night. He was 81.

FILE - In this Oct. 24, 2017 file photo, Kenny Rogers poses with his star on the Music City Walk of Fame in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81. (AP Photo/Mark Humphrey, File)© Provided by Associated Press FILE - In this Oct. 24, 2017 file photo, Kenny Rogers poses with his star on the Music City Walk of Fame in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81. (AP Photo/Mark Humphrey, File)
He died at home in Sandy Springs, Georgia, representative Keith Hagan told The Associated Press. He was under hospice care and died of natural causes, Hagan said.

The Houston-born performer with the husky voice and silver beard sold tens of millions of records, won three Grammys and was the star of TV movies based on “The Gambler” and other songs, making him a superstar in the ‘70s and ’80s. Rogers thrived for some 60 years before retired from touring in 2017 at age 79. Despite his crossover success, he always preferred to be thought of as a country singer.

“You either do what everyone else is doing and you do it better, or you do what no one else is doing and you don’t invite comparison,” Rogers told The Associated Press in 2015. “And I chose that way because I could never be better than Johnny Cash or Willie or Waylon at what they did. So I found something that I could do that didn’t invite comparison to them. And I think people thought it was my desire to change country music. But that was never my issue.”

In this Oct. 27, 2013, file photo, country music star Kenny Rogers thanks the audience at the ceremony for the 2013 inductions into the Country Music Hall of Fame in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81. (AP Photo/Mark Zaleski, File)© Provided by Associated Press ADDS YEAR - FILE - In this Oct. 27, 2013, file photo, country music star Kenny Rogers thanks the audience at the ceremony for the 2013 inductions into the Country Music Hall of Fame in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81.
His “Islands in the Stream” duet partner Dolly Parton posted a video on Twitter on Saturday morning, choking up as she held a picture of the two of them together. “I loved Kenny with all my heart and my heart is broken and a big ole chunk of it is gone with him today," Parton said in the video.

“Kenny was one of those artists who transcended beyond one format and geographic borders,” says Sarah Trahern, chief executive officer of the Country Music Association. “He was a global superstar who helped introduce country music to audiences all around the world."

This May 17, 1989 file photo shows Kenny Rogers posing for a portrait in Los Angeles.   Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020.  (AP Photo/Bob Galbraith, File)© Provided by Associated Press FILE - This May 17, 1989 file photo shows Kenny Rogers posing for a portrait in Los Angeles. Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/Bob Galbraith, File)
Rogers was a five-time CMA Award winner, as well as the recipient of the CMA's Willie Nelson Lifetime Achievement Award in 2013, the same year he was inducted into the Country Music Hall of Fame. He received 10 awards from the Academy of Country Music. He sold more than 47 million records in the United States alone, according to the Recording Industry Association of America.

A true rags-to-riches story, Rogers was raised in public housing in Houston Heights with seven siblings. As a 20-year-old, he had a gold single called “That Crazy Feeling,” under the name Kenneth Rogers, but when that early success stalled, he joined a jazz group, the Bobby Doyle Trio, as a standup bass player.

This Feb. 20, 1978 file photo shows Kenny Rogers at his home in Brentwood, Calif.   Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020.  (AP Photo/Wally Fong, File)© Provided by Associated Press FILE - This Feb. 20, 1978 file photo shows Kenny Rogers at his home in Brentwood, Calif. Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/Wally Fong, File)
But his breakthrough came when he was asked to join the New Christy Minstrels, a folk group, in 1966. The band reformed as First Edition and scored a pop hit with the psychedelic song, “Just Dropped In (To See What Condition My Condition Was In).” Rogers and First Edition mixed country-rock and folk on songs like “Ruby, Don’t Take Your Love To Town,” a story of a Vietnam veteran begging his girlfriend to stay. 

After the group broke up in 1974, Rogers started his solo career and found a big hit with the sad country ballad “Lucille,” in 1977, which crossed over to the pop charts and earned Rogers his first Grammy. Suddenly the star, Rogers added hit after hit for more than a decade.

“The Gambler,” the Grammy-winning story song penned by Don Schlitz, came out in 1978 and became his signature song with a signature refrain: “You gotta know when to hold ‘em, know when to fold ’em.” The song spawned a hit TV movie of the same name and several more sequels featuring Rogers as professional gambler Brady Hawkes, and led to a lengthy side career for Rogers as a TV actor and host of several TV specials.

FILE - In this June 9, 2012, file photo, Kenny Rogers performs at the 2012 CMA Music Festival in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81. (Photo by Wade Payne/Invision/AP, File)© Provided by Associated Press FILE - In this June 9, 2012, file photo, Kenny Rogers performs at the 2012 CMA Music Festival in Nashville, Tenn. Actor-singer Kenny Rogers, the smooth, Grammy-winning balladeer who spanned jazz, folk, country and pop with such hits as “Lucille,” “Lady” and “Islands in the Stream” and embraced his persona as “The Gambler” on record and on TV died Friday night, March 20, 2020. He was 81. (Photo by Wade Payne/Invision/AP, File)
“I think the best that any songwriter could hope for is to have Kenny Rogers sing one of your songs,” said Schlitz, who also co-wrote the other Parton-Rogers duet “You Can’t Make Old Friends.” “He gave so many career songs to so many of us.”

Schlitz noted that some of Rogers’ biggest hits were songs that had been recorded previously, but his versions became the most popular. “The Gambler” had been recorded six other times before Rogers and “Ruby Don’t Take Your Love to Town,” by Mel Tillis, was also recorded by other artists before Rogers.

Other hits included “You Decorated My Life,” “Every Time Two Fools Collide” with Dottie West, “Don’t Fall In Love with a Dreamer” with Kim Carnes, and “Coward of the County.” One of his biggest successes was “Lady,” written by Lionel Richie, a chart topper for six weeks straight in 1980. Richie said in a 2017 interview with the AP that he often didn’t finish songs until he had already pitched them, which was the case for “Lady.”

FILE - In this March 22, 1979 file photo,   Kenny Rogers, center, rolls the dice at Regine's in New York.   Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020.  (AP Photo/Richard Drew, File)© Provided by Associated Press FILE - In this March 22, 1979 file photo, Kenny Rogers, center, rolls the dice at Regine's in New York. Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/Richard Drew, File)
“In the beginning, the song was called, ‘Baby,'” Richie said. “And because when I first sat with him, for the first 30 minutes, all he talked about was he just got married to a real lady. A country guy like him is married to a lady. So, he said, ‘By the way, what’s the name of the song?’” Richie replies: “Lady.”

FILE - In this Sept. 27, 1983 file photo, Country Music singers Dolly Parton and Kenny Rogers rehearse a song for their appearance on the TV show "Live... And in Person" in Los Angeles.  Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020.  (AP Photo/Doug Pizac, File)© Provided by Associated Press FILE - In this Sept. 27, 1983 file photo, Country Music singers Dolly Parton and Kenny Rogers rehearse a song for their appearance on the TV show "Live... And in Person" in Los Angeles. Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/Doug Pizac, File)
Over the years, Rogers worked often with female duet partners, most memorably, Dolly Parton. The two were paired at the suggestion of the Bee Gees’ Barry Gibb, who wrote “Islands in the Stream.”

“Barry was producing an album on me and he gave me this song,” Rogers told the AP in 2017. “And I went and learned it and went into the studio and sang it for four days. And I finally looked at him and said, ‘Barry, I don’t even like this song anymore.’ And he said, ‘You know what we need? We need Dolly Parton.’ I thought, ‘Man, that guy is a visionary.’”

In this Feb. 28, 1980 file photo, Kenny Rogers holds a Grammy Award he received during presentation in Los Angles.  Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/McLendon, File)© Provided by Associated Press FILE- In this Feb. 28, 1980 file photo, Kenny Rogers holds a Grammy Award he received during presentation in Los Angles. Rogers, who embodied “The Gambler” persona and whose musical career spanned jazz, folk, country and pop, has died at 81. A representative says Rogers died at home in Georgia on Friday, March 20, 2020. (AP Photo/McLendon, File)
Coincidentally, Parton was actually in the same recording studio in Los Angeles when the idea came up.

“From the moment she marched into that room, that song never sounded the same,” Rogers said. “It took on a whole new spirit.”

The two singers toured together, including in Australia and New Zealand in 1984 and 1987, and were featured in a HBO concert special. Over the years the two would continue to record together, including their last duet, “You Can’t Make Old Friends,” which was released in 2013. Parton reprised “Islands in the Stream” with Rogers during his all-star retirement concert held in Nashville in October 2017.

Rogers invested his time and money in a lot of other endeavors over his career, including a passion for photography that led to several books, as well as an autobiography, “Making It With Music.” He had a chain of restaurants called Kenny Rogers Roasters and was a partner behind a riverboat in Branson, Missouri. He was also involved in numerous charitable causes, among them the Red Cross and MusiCares, and was part of the all-star “We are the World” recording for famine relief.



By the '90s, his ability to chart hits had waned, although he still remained a popular live entertainer with regular touring. Still he was an inventive businessman and never stopped trying to find his way back onto the charts.
At the age of 61, Rogers had a brief comeback on the country charts in 2000 with a hit song “Buy Me A Rose,” thanks to his other favorite medium, television. Producers of the series “Touched By An Angel” wanted him to appear in an episode, and one of his managers suggested the episode be based on his latest single. That cross-promotional event earned him his first No. 1 country song in 13 years.

Rogers is survived by his wife, Wanda, and his sons Justin, Jordan, Chris and Kenny Jr., as well as two brothers, a sister and grandchildren, nieces and nephews, his representative said. The family is planning a private service “out of concern for the national COVID-19 emergency,” a statement posted early Saturday read. A public memorial will be held at a later date.
"""


# In[9]:


for i, res in enumerate(tree.search([article_text], cosine_similarity)):
    if i % 2 == 0: 
        print("Category:", res[1],"(similarity {})".format(res[0]))
    else:
        print("Page:", res[1],"(similarity {})".format(res[0]))


# In[ ]:


for i, n in enumerate(tree.root.children[1].children):
    print(i, n)


# In[ ]:


def get_correlation_matrix(node):
    try:
        category_vec = []
        for n in node.children:
            mean_vec = np.mean(n.vectors, axis=0)
            if mean_vec.shape == (75000,):
                mean_vec = mean_vec.reshape((1,75000))
            category_vec.append(mean_vec)
            
        correlation = []
        for n in category_vec:
            corr = []
            for neigh in category_vec:
                corr.append(cosine_similarity(n, neigh)[0,0])
            correlation.append(corr)
        if len(correlation) == 0:
            return np.array([[0]]), None
        category_labels = []
        for n in node.children:
            category_labels.append(n.category)
        return correlation, category_labels
    except ValueError:
        print(n, neigh)


# In[ ]:


correlation_means = dict()
for node in tree.root.children:
    correlation_means[node.category] = np.mean(get_correlation_matrix(node)[0])
    for node_1 in node.children:
        correlation_means[node_1.category] = np.mean(get_correlation_matrix(node_1)[0])


# In[ ]:


new_categories = set()
for node in correlation_means.keys():
    if correlation_means[node] < 0.1 and correlation_means[node] != 0.0:
        print(node, correlation_means[node])
        new_categories.add(node)


# In[ ]:


with open("additional_tree.sh", "w") as fp:
    for cat in new_categories:
        fp.write("python pwb.py category tree -depth:2 <<EOF\n{}\nadditional_trees/{}\nEOF\n".format(cat, cat.replace(' ','_').replace('-','')))


# In[ ]:


import matplotlib.pyplot as plt
import seaborn as sns
correlation, correlation_labels = get_correlation_matrix(tree.root.children[8].children[16])
fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(correlation, xticklabels=correlation_labels, yticklabels=correlation_labels)


# In[ ]:


for i, node in enumerate(tree.root.children[1].children[11].children):
    print(i, node)


# In[ ]:


import seaborn as sns
import matplotlib.pyplot as plt

correlation, correlation_labels = get_correlation_matrix(tree.root)
fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(correlation, xticklabels=correlation_labels, yticklabels=correlation_labels)


# In[ ]:


np.mean(correlation)


# In[ ]:


category_vec = []
for node in tree.root.children[0].children[0].children:
    category_vec.append(np.mean(node.vectors, axis=0).reshape(1,75000))
    
correlation = []
for node in category_vec:
    corr = []
    for neigh in category_vec:
        corr.append(cosine_similarity(node, neigh)[0,0])
    correlation.append(corr)
category_labels = []
for node in tree.root.children[0].children[0].children:
    category_labels.append(node.category)
fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(correlation, xticklabels=category_labels, yticklabels=category_labels)


# In[ ]:


print(category_vec[0].shape)

