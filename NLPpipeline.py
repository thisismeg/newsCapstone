#!/usr/bin/env python
# coding: utf-8

# In[40]:


from nltk.util import ngrams
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from collections import Counter


# In[89]:


class Pipeline:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.tokenizer = RegexpTokenizer(r'\w+')
        
    def transform(self, text):
        words = self.tokenizer.tokenize(text)
        stemmed_tokens = [self.stemmer.stem(word) for word in words if word not 
                          in list(stopwords.words('english'))]
        
        unigrams = list(ngrams(stemmed_tokens, 1))
        bigrams = list(ngrams(stemmed_tokens, 2))
        unigrams_dict = dict(Counter(unigrams))
        bigrams_dict = dict(Counter(bigrams))
        
        fingerprint_dict = dict()
        fingerprint_dict.update(unigrams_dict)
        fingerprint_dict.update(bigrams_dict)
        
        return fingerprint_dict

