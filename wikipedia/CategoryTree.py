import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import numpy as np 

MAX_FEATURES = 75000

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
                    
    def vectorize(self):
        for node in self.root.children:
            node_child, length = np.zeros((1, MAX_FEATURES)), 0
            for node_1 in node.children:
                node_1_child, length_1 = np.zeros((1, MAX_FEATURES)), 0
                for node_2 in node_1.children:
                    try:
                        node_2.vectors = self.vectorizer.transform(node_2.texts)
                        node_1_child += np.mean(node_2.vectors, axis=0)
                        node_child += np.mean(node_2.vectors, axis=0)
                        length_1 += 1
                        length += 1
                    except ValueError:
                        node_2.vectors = np.zeros((1, MAX_FEATURES))
                try:
                    node_1.vectors = self.vectorizer.transform(node_1.texts)
                    node_child += np.mean(node_1.vectors, axis=0)
                    length += 1
                except ValueError:
                    if length_1 > 0:
                        node_1.vectors = node_1_child / length_1
                    else:
                        node_1.vectors = np.zeros((1, MAX_FEATURES))
            try:
                node.vectors = self.vectorizer.transform(node.texts)
            except ValueError:
                if length > 0:
                    node.vectors = node_child / length
                else:
                    node.vectors = np.zeros((1, MAX_FEATURES))
                
    def search(self, words, similarity_metric):
        input_vector = self.vectorizer.transform(words)
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
            
if __name__ == "__main__":
    tree = CategoryTree(TfidfVectorizer(stop_words=list(stopwords.words('english')),
                                        max_features=MAX_FEATURES))
    tree.load_json('search_tree_with_text.json')



    article_text = """
    Israeli Prime Minister Benjamin Netanyahu and his chief rival on Monday signed an agreement to form an “emergency” government, their parties announced in a joint statement.

    The deal between Netanyahu’s Likud Party and former military chief Benny Gantz’s Blue and White ends months of political paralysis and averts what would have been a fourth consecutive election in just over a year.

    After March 2 elections ended in a stalemate, the two leaders agreed late last month to try to form an “emergency” unity Cabinet to cope with the burgeoning coronavirus crisis.

    Ending weeks of negotiations, the sides announced a deal on Monday. Had they failed, the country likely would have been forced into another election.

    Terms of the agreement weren’t immediately announced. But Israeli media said it called for a three-year period — with Netanyahu serving as prime minister for the first half and Gantz taking the job for the second half.
    """

    for i, res in enumerate(tree.search([article_text], cosine_similarity)):
        if i % 2 == 0: 
            print("Category:", res[1],"(similarity {})".format(res[0]))
        else:
            print("Page:", res[1],"(similarity {})".format(res[0]))






