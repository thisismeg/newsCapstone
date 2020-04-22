import json

def load_json(json_file):
    with open(json_file) as f:
        data = json.load(f)
    return data

def convert_fingerprint(fingerprint_index, wordDict, entityDict):
    converted_fingerprint = {}
    if fingerprint_index is not None:
        for key in fingerprint_index:
            if key in ('wordCounts', 'bigramCounts'):
                tmp = {}
                for sub_key in fingerprint_index[key]:
                    tmp[wordDict[sub_key]]=fingerprint_index[key][sub_key]
            else:
                tmp = {}
                for sub_key in fingerprint_index[key]:
                    tmp[entityDict[sub_key]['uniqueId']]=fingerprint_index[key][sub_key]
            converted_fingerprint[key]=tmp
    return converted_fingerprint

def convert_fingerprint_event(fingerprint_index, wordDict, entityDict):
    converted_fingerprint = {}
    if fingerprint_index is not None:
        for key in fingerprint_index:
            print (key)
            tmp =''
            if key in ('words'):
                tmp = {}
                for sub_key in fingerprint_index[key]['cloud']:
                    tmp[wordDict[sub_key]]=fingerprint_index[key]['cloud'][sub_key]
            if key in ('entities'):
                tmp = {}
                for sub_key in fingerprint_index[key]['cloud']:
                    tmp[entityDict[sub_key]['uniqueId']]=fingerprint_index[key]['cloud'][sub_key]
                pass
            converted_fingerprint[key]=tmp
    return converted_fingerprint

def word_entity_dict(raw_json):
    word_dict = raw_json['wordDict']
    entity_dict = raw_json['entityDict']
    return word_dict, entity_dict

def article_information_extraction(file_record, word_dict, entity_dict):
    article_infor = {}
    article_infor['raw_title'] = file_record['Item3']['content']['title']
    article_infor['raw_text'] = file_record['Item3']['content']['text']
    article_infor['raw_title_orginal'] = file_record['Item3']['original_title']
    article_infor['title_fingerprint_index'] = file_record['Item3']['titleFingerprint']
    article_infor['text_fingerprint_index'] = file_record['Item3']['textFingerprint']
    article_infor['title_fingerprint_val'] = convert_fingerprint(article_infor['title_fingerprint_index'], word_dict, entity_dict)
    article_infor['text_fingerprint_val'] =convert_fingerprint(article_infor['title_fingerprint_index'], word_dict, entity_dict)
    
    return article_infor

def event_information_extraction(event_record, word_dict, entity_dict):
    event_dict = {}
    event_dict['events_idx'] = {key: event_record['mainEvent'][key] for key in event_record['mainEvent'] if key in ['words', 'entities'] }
    event_dict['events_val'] = convert_fingerprint_event(event_dict['events_idx'], word_dict, entity_dict)
    event_articles['events_articles'] = event_dict['eventArticles']
    
    return event_dict