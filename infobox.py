import urllib, json
import matching
import pprint
from collections import OrderedDict
from printable import print_table

api_key = ''

def run(api_k, query):
    global api_key
    api_key = api_k
    data, type_list,  type_list_name= topic(search(query), matching.accepted_type_list)

    result,type_list_name = assemble_infobox(data, type_list, matching.information_map,type_list_name)
    print_table(result,type_list_name)

#Infobox Creation
def search(query):
    service_url = 'https://www.googleapis.com/freebase/v1/search'
    params = {
        'query': query,
        'key': api_key}
    url = service_url + '?' + urllib.urlencode(params)
    response = json.loads(urllib.urlopen(url).read())['result']
    result_mid = []

    for result in response:
        result_mid.append(result['mid'])
    return result_mid
 
#return collected raw data and type list
def topic(result_mid, accepted_type_list):
    service_url = 'https://www.googleapis.com/freebase/v1/topic'
    params = {
        'key': api_key
    }
    for topic_id in result_mid:
        url = service_url + topic_id + '?' + urllib.urlencode(params)
        topic = json.loads(urllib.urlopen(url).read())
        type_list = []
        type_list_name = []
        re_types_list = topic['property']['/type/object/type']['values']
        for ac_types in accepted_type_list.keys():
            for re_types in re_types_list:
                if(re_types['id'].encode("ascii") == ac_types):
                    type_list.append(ac_types)

        valid_type = valid_topic(type_list, accepted_type_list)
        valid_type_list = cleanup_type(valid_type)
        print valid_type_list
        for ac_types in valid_type_list:
             type_list_name.append(accepted_type_list[ac_types])
        type_list_name = list(set(type_list_name))
        if len(type_list_name) is not 0:
            return topic, valid_type_list, type_list_name
    return {}, [], []

#detect conflict in types and keep only reasonable ones
def cleanup_type(valid_type_list):
    set_A = ['/people/person','/people/deceased_person','/book/author','/film/actor','/tv/tv_actor','/organization/organization_founder','/business/board_member']
    set_B = ['/sports/sports_league']
    set_C = ['/sports/sports_team','/sports/professional-_sports_team']
    IsPpl = True
    for item in valid_type_list:
        if item in set_B or item in set_C:
            IsPpl = False
    if not IsPpl:
        for item in valid_type_list:
            if item in set_A:
                valid_type_list.remove(item)

    return valid_type_list

#select valid type from compaing between both list
def valid_topic(type_list, accepted_type_list):
    valid_type_list=[]
    for types in type_list:
        if(types in accepted_type_list):
            valid_type_list.append(types)
    return valid_type_list

#transoform raw data into our data structure
def assemble_infobox(data, typeid_list, information_map,type_list_name):
    result = OrderedDict()
    for one_type in typeid_list:
        info_dict = information_map[one_type]
        for info_keys, info_values in info_dict.iteritems():
            # non-nested dict
            if(type(info_values) is str):
                tmp_text=[]
                try:
                    for text_list in data['property'][info_keys]['values']:
                        val = text_list['text']
                        try:
                            val = text_list['value']
                        except KeyError:
                            pass
                        tmp_text.append(val.replace('\n', ' '))
                except KeyError:
                    pass
                    # tmp_text.append('')
                result[info_values] = tmp_text
             # nested dict
            if(type(info_values) is dict):
                # if nested property only has one key, treat it as outer property
                if(len(info_values['children']) == 1):
                    for nested_key, nested_value in info_values['children'].iteritems():
                        tmp_text=[]
                        for text_list in data['property'][info_keys]['values']:
                            try:
                                for inner_text_list in text_list['property'][nested_key]['values']:
                                    val = inner_text_list['text']
                                    try:
                                        val = inner_text_list['value']
                                    except KeyError:
                                        pass
                                    tmp_text.append(val.replace('\n', ' '))
                            except KeyError:
                                tmp_text.append('')
                        result[info_values['name']] = tmp_text
                # if nested property only has more than one key, add name as key
                else:
                    # result[info_values['name']] = {}
                    # for nested_key, nested_value in info_values['children'].iteritems():
                    #     tmp_text=[]
                    #     for text_list in data['property'][info_keys]['values']:
                    #         try:
                    #             for inner_text_list in text_list['property'][nested_key]['values']:
                    #                 val = inner_text_list['text']
                    #                 try:
                    #                     val = inner_text_list['value']
                    #                 except KeyError:
                    #                     pass
                    #                 tmp_text.append(val)
                    #         except KeyError:
                    #             tmp_text.append('')
                    #     result[info_values['name']][nested_value] = tmp_text

                    result[info_values['name']] = []
                    try:
                        for text_list in data['property'][info_keys]['values']:
                            tmp_dict = {}
                            for nested_key, nested_value in info_values['children'].iteritems():
                                try:
                                    if len(text_list['property'][nested_key]['values']) == 0:
                                        val = ''
                                    else:

                                        total=''

                                        for inner_most_dict in text_list['property'][nested_key]['values']:
                            
                                            val = inner_most_dict['text']
                                            try:
                                                val = inner_most_dict['value']
                                            except KeyError:
                                                pass

                                            total+=val + ","

                                    tmp_dict[nested_value] = total.strip(",").replace('\n', ' ')

                                except KeyError:
                                    tmp_dict[nested_value] = ''
                            result[info_values['name']].append(tmp_dict)
                    except KeyError:
                        pass


    return result,type_list_name

 

#Question Answering



if __name__ == '__main__': run('AIzaSyB-LJI6QQ9P_D1WyKuCLT6yABME20lrYwM', 'NFL')
 

