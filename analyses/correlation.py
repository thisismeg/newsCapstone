import seaborn as sns
import matplotlib.pyplot as plt

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

correlation_means = dict()
for node in tree.root.children:
    correlation_means[node.category] = np.mean(get_correlation_matrix(node)[0])
    for node_1 in node.children:
        correlation_means[node_1.category] = np.mean(get_correlation_matrix(node_1)[0])

new_categories = set()
for node in correlation_means.keys():
    if correlation_means[node] < 0.1 and correlation_means[node] != 0.0:
        print(node, correlation_means[node])
        new_categories.add(node)

correlation, correlation_labels = get_correlation_matrix(tree.root.children[8].children[16])
fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(correlation, xticklabels=correlation_labels, yticklabels=correlation_labels)

correlation, correlation_labels = get_correlation_matrix(tree.root)
fig, ax = plt.subplots(figsize=(15,10))
sns.heatmap(correlation, xticklabels=correlation_labels, yticklabels=correlation_labels)


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