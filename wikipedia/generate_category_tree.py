import os
import re
import json
import mwparserfromhell as wp
from tqdm import tqdm



wiki_pages = json.load(open('files.json','r'))
wiki_pages = json.loads(wiki_pages)

cat_pages = json.load(open('categories_pages.json','r'))
cat_pages = json.loads(cat_pages)

dead_pages = []
for page in tqdm(wiki_pages.keys()):
    try:
        with open(wiki_pages[page], 'r') as fp:
            continue
    except:
        dead_pages.append(page)
        
for page in dead_pages:
    del wiki_pages[page]

class CategoryNode:
    def __init__(self, category, parent):
        self.category = category
        self.parent = parent 
        self.children = []
        filename = category.replace(' ', '_').replace('-','').replace('&','_').replace('/','_').replace("(","").replace(")","")
        self.final_pages = []
        if category == 'Root':
            self.pages = None
            self.texts = None
        else:
            self.pages = self.add_pages(category, filename)
            self.add_texts()
        
    def add_child(self, node):
        self.children.append(node)
        
    def add_pages(self, category, file):
        pages = set([self.category])
        try:
            for page in cat_pages[category]:
                pages.add(page)
        except KeyError:
            pass
        
        try:
            fp = open("category_files/"+file, 'r')
            for line in fp:
                if len(line) > 1:
                    pages.add(re.search('[0-9]+ (.*)', line).group(1))
        except FileNotFoundError:
            pass
        
        return pages
        
        
    def add_texts(self):
        self.texts = []
        removals = []
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
                self.final_pages.append(page)
            except KeyError:
                try:
                    if page[-1] == 's':
                        fp = open(wiki_pages[page[:-1]], 'r')
                        text = fp.read()
                        fp.close()
                        parser = wp.parse(text)
                        sections = parser.strip_code().split('\n')
                        text = ""            
                        for sec in sections:
                            if '.' in sec:
                                text += sec + ' '
                        self.texts.append(text)
                        self.final_pages.append(page)
                except KeyError:
                    pass
                        
    def delete_child(self, cat):
        del_index = None
        for i, child in enumerate(self.children):
            if child.category == cat:
                del_index = i 
                break
        del self.children[del_index]
        
    def __str__(self):
        return self.category

fp = open("root_tree", "r")
level_one = None
level_two = None
root_node = CategoryNode("Root", None)
fp.readline()
skip_node = False
nodes = set()
for line in tqdm(fp):
    if '####' in line:
        continue
    hashs = line.split(' [[')[0]
    cat = re.findall("\[\[:Category:(.*?)\|", line)[0] 
    filename = cat.replace(' ', '_').replace('-','').replace('&','_').replace('/','_')
    if hashs == "#":
        node = CategoryNode(cat, root_node)
        root_node.add_child(node)
        level_one = node
    elif hashs == "##":
        skip_node = False
        if filename in os.listdir('additional_trees/'):
            skip_node = True
            add_node = None
            with open('additional_trees/'+filename) as np:
                np.readline()
                for line in np:
                    if '###' in line:
                        continue
                    hashs = line.split(' [[')[0]
                    cat = re.findall("\[\[:Category:(.*?)\|", line)[0]
                    filename = cat.replace(' ', '_').replace('-','').replace('&','_').replace('/','_')
                    if hashs == "#":
                        node_1 = CategoryNode(cat, level_one)
                        level_one.add_child(node)
                    if hashs == "##":
                        node_2 = CategoryNode(cat, node_1)
                        node_1.add_child(node_2)
                        if len(node_2.pages) == 0:
                            node_1.delete_child(cat)
        else:
            node = CategoryNode(cat, level_two)
            level_one.add_child(node)
            level_two = node
             
    elif hashs == '###' and skip_node == False:
        node = CategoryNode(cat, level_two)
        level_two.add_child(node)
        if len(node.pages) == 0:
            level_two.delete_child(cat)


unchecked_nodes = [(child, []) for child in root_node.children]
copy = dict()
while len(unchecked_nodes) > 0:
    node, path = unchecked_nodes[0]
    unchecked_nodes = unchecked_nodes[1:]

    section = copy
    for p in path:
        section = section[p]
        
    section[cat] = dict()
    section[cat]['pages'] = node.pages
    section[cat]['texts'] = node.texts

    node_children = [(child, path + [node.category]) for child in node.children]
    unchecked_nodes += node_children
        
fp = open('search_tree_with_text', 'w')           
json_str = json.dumps(copy)
json.dump(json_str, fp)

