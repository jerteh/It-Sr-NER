import spacy
import os
import pathlib
from helper import text_chunks, replace_string
from lxml import etree
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import folium
import json
import html
import requests
from time import sleep


dir_x = str(pathlib.Path(__file__).parent.resolve())
conf = pd.read_csv(dir_x + "/config/lng_config.csv", delimiter='\t').set_index('lng')
conf = conf.replace({np.nan: None})
languages = conf.axes[0].tolist()
languages = [x for x in languages if conf.loc[x]['map_ner_types'] is not None]
tags = ['PERS', 'LOC', 'ORG', 'DEMO', 'EVENT', 'WORK']
nlps = {}
dic_remove_tags = {}
dic_tags = {}
# 300 segments for a chunk
chunk_size = 300
# text up to 5000 characters without chunking
text_size_without_chunking = 5000
# NEL model
nel_model = "sr_SRPCNNEL"
# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")
with open(dir_x + "/geocache.json", "r", encoding="utf-8") as gc:
    geocache = json.load(gc)

for lng in languages:
    if conf.loc[lng]['remove_types']:
        dic_remove_tags[lng] = conf.loc[lng]['remove_types'].split(',')
    if conf.loc[lng]['map_ner_types']:
        dic_tags[lng] = conf.loc[lng]['map_ner_types'].split(',')


def load_model(mname):
    try:
        x = spacy.load(mname).from_disk(dir_x + "/models/" + mname)
    except:
        try:
            x = spacy.load(dir_x + "/models/" + mname)
        except:
            d = [y for y in os.listdir(dir_x + "/models/" + mname) if mname in y]
            x = spacy.load(dir_x + "/models/" + mname + "/" + d[0])
    return x


nlp_nel = load_model(nel_model)
# for local
# nlp_nel.add_pipe('opentapioca', config={"url": OpenTapiocaAPI})
# nlp_nel.add_pipe("sentencizer")
# nlp_nel.add_pipe("entityLinker", last=True)


# user for NER+NEL
def do_nel(text):
    # create list of tuples with entities text and list of QID and descriptions in wikidata - new function
    # tuple: (Beograd, [Q371, 'City in Serbia'])
    entities = []
    result = {}
    if len(text) < text_size_without_chunking:
        doc_nel = nlp_nel(text)
        entities += [x for x in doc_nel.ents if x.kb_id_ != 'NIL']
    else:
        # split text into chunks with max chunk_size (= 300) lines of text
        chunks = text_chunks(text, chunk_size)
        for chunk in chunks:
            text_chunk = '\n'.join(chunk)
            #  doc object with applied nlp_nel on input text
            doc_nel = nlp_nel(text_chunk)
            entities += [x for x in doc_nel.ents if x.kb_id_ != 'NIL']

    return {x.orth_: x for x in entities}


# optimizovati
def apply_NEL_model_mono(text):
    marked_text = text

    if len(text) < text_size_without_chunking:
        text_chunk_out = apply_NEL_model_mono_onchunk(marked_text)
        text_ner = text_chunk_out
    else:
        chunks = text_chunks(marked_text, chunk_size)
        text_ner = ''
        for chunk in chunks:
            text_chunk = '\n'.join(chunk)
            text_chunk_out = apply_NEL_model_mono_onchunk(text_chunk)
            text_ner = text_ner + text_chunk_out + '\n'
    return text_ner


def apply_NEL_model_mono_onchunk(text_chunk):
    move_p = 0
    # apply NEL model to input text
    Dict = do_nel(text_chunk)
    for entx in Dict.keys():
        ent = Dict.get(entx)
        QID = ent.kb_id_
        Desc = fetch_name_and_definition_from_wikipedia(QID)
        start = move_p + ent.start_char
        end = move_p + ent.end_char
        new = '<WDT ref="https://www.wikidata.org/wiki/' + QID + '"' + ' label="' + ent.label_ + '" desc="' + str(
            Desc) + '"' + '>' + ent.orth_ + '</WDT>'
        text_chunk = replace_string(text_chunk, new, start, end)
        up = len(new)+start-end
        move_p += up
    return text_chunk


# optimizovati
def apply_NER_NEL_model_mono(text, lng):
    global nlps
    if lng not in nlps:
        mname = conf.loc[lng, 'lng_model']
        nlps[lng] = load_model(mname)
    nlp = nlps[lng]

    lst_remove_tags = dic_remove_tags[lng]
    # doc object with applied nlp on input text
    doc = nlp(text)

    # call function tapioca_nel and get dictionary
    Dict = do_nel(text)
    # move position
    move_p = 0
    marked_text = text
    for ent in doc.ents:
        if ent.label_ not in lst_remove_tags:
            start = move_p + ent.start_char
            end = move_p + ent.end_char
            if ent.text in Dict.keys():
                QID = ent.kb_id_
                Desc = fetch_name_and_definition_from_wikipedia(QID)
                new = '<' + ent.label_ + ' ref="https://www.wikidata.org/wiki/' + QID + '"' + ' desc="' + str(
                    Desc) + '"''>' + ent.text + '</' + ent.label_ + '>'
                marked_text = replace_string(marked_text, new, start, end)
            else:
                new = '<' + ent.label_ + '>' + ent.text + '</' + ent.label_ + '>'
                marked_text = replace_string(marked_text, new, start, end)
            up = len(new)+start-end
            move_p += up
    marked_text = map_tags(marked_text, lng)
    return marked_text


# tagset harmonisation: mapping NER labels to same tagset
def map_tags(marked_text, lng):
    lst_tags = dic_tags[lng]
    i = 0
    f = marked_text
    for ne_tags in lst_tags:
        for tag in ne_tags.split('+'):
            if tag != tags[i] and tag != '':
                f = f.replace("<" + tag, "<" + tags[i])
                f = f.replace("</" + tag, "</" + tags[i])
        i += 1
    return f


# apply NER and annotate with NER tags
def apply_NER_model_mono(text, lng):
    global nlps
    if lng not in nlps:
        mname = conf.loc[lng, 'lng_model']
        nlps[lng] = load_model(mname)
    nlp = nlps[lng]

    lst_remove_tags = dic_remove_tags[lng]
    # apply NER model to input text
    doc = nlp(text)
    # the number of characters by which we move position of label
    move_p = 0
    marked_text = text
    for ent in doc.ents:
        if ent.label_ not in lst_remove_tags:
            start = move_p + ent.start_char
            end = move_p + ent.end_char
            new = '<' + ent.label_ + '>' + ent.text + '</' + ent.label_ + '>'
            marked_text = replace_string(marked_text, new, start, end)
            up = len(new)+start-end
            move_p += up
    marked_text = map_tags(marked_text, lng)
    return marked_text


def monolingual_ner_nel(data, lng, with_ner=True, with_nel=False):
    if with_nel and with_ner:
        x = apply_NER_NEL_model_mono(data, lng)
    elif with_nel:
        x = apply_NEL_model_mono(data)
    elif with_ner:
        x = apply_NER_model_mono(data, lng)
    else:
        x = data
    return html.unescape(x)


def bilingual_ner_nel(data, with_ner=True, with_nel=False):
    el = etree.fromstring(data)
    tus = el.xpath("//*[local-name()='tu']")
    for tu in tus:
        tuvs = tu.xpath("*[local-name()='tuv']")
        for tuv in tuvs:
            lng = tuv.xpath("./@xml:lang", namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})[0]
            data = tuv.getchildren()[0].text  # tuv/seg
            # apply model
            text_ner = monolingual_ner_nel(data, lng, with_ner, with_nel)

            # sinhronize content of tuv/seg
            tuv.getchildren()[0].text = text_ner

    # read xml as string
    xml_str = etree.tostring(el, encoding='unicode')
    # replace special characters
    xml_str = xml_str.replace("&gt;", ">").replace("&lt;", "<")
    return xml_str
    # except:
    #   return "Submited file was not properly formatted :(("


# 1.10.2022 Ranka
# create datafrema with entities annotate with NER tags and NEL attributes
# fuction created 27.09.2022.
# text - content from input file
# nlp - language object (sr, it)
# lst_remove_tags - list of tags wich will be removed from tagset
def df_entities_NER_NEL(text, lng, doc=None):
    if not doc:
        global nlps
        if lng not in nlps:
            mname = conf.loc[lng, 'lng_model']
            nlps[lng] = load_model(mname)
        nlp = nlps[lng]
        lst_ent = []
        lst_remove_tags = dic_remove_tags[lng]
        lst_tags = dic_tags[lng]
        # doc object with applied nlp on input text
        doc = nlp(text)
        # call function tapioca_nel and get dictionary
        Dict = do_nel(text)

        for ent in doc.ents:
            if ent.label_ not in lst_remove_tags:
                if ent.text in Dict.keys() and ent.label_ in lst_tags[1]:
                    lst_ent.append(ent.text)
        lst_ent = list(set(lst_ent))
    else:
        lst_ent = []
        for ent in doc.ents:
            if ent.text in doc.keys() and ent.label_ == 'LOC':
                lst_ent.append(ent.text)
        lst_ent = list(set(lst_ent))

    return lst_ent


def get_entities(text, lng, doc, tmx=False):
    if tmx:
        lst_ent = []
        el = etree.fromstring(text)
        tus = el.xpath("//*[local-name()='tu']")
        for tu in tus:
            tuvs = tu.xpath("*[local-name()='tuv']")
            for tuv in tuvs:
                lnx = tuv.xpath("./@xml:lang", namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})[0]
                data = tuv.getchildren()[0].text  # tuv/seg
                lst_ent.extend(df_entities_NER_NEL(data, lnx))
    else:
        lst_ent = df_entities_NER_NEL(text, lng, doc)

    data = {'entity': lst_ent}
    entities_df = pd.DataFrame(data)
    return entities_df


# create latitude and longitude
# entities_df dataframe with entities
def create_lat_lng(ent_df):
    # ent_df = pd.DataFrame()
    # ent_df = entities_df
    loc_dfs = pd.DataFrame()
    loc_not_find = []
    for entity_unique in ent_df['entity'].unique().tolist():
        try:
            loc_dict = getLocation(entity_unique)
            loc_df = pd.DataFrame(loc_dict, index=[0])
            loc_dfs = pd.concat([loc_dfs, loc_df])
        except:
            loc_not_find.append(entity_unique)
            pass
    return loc_dfs


def getLocation(entity_unique):
    global geocache
    if entity_unique not in geocache:
        getLoc = loc.geocode(entity_unique)
        geocache[entity_unique] = {'lat': getLoc.latitude, 'long': getLoc.longitude}
    return {'entity': entity_unique, 'lat': geocache[entity_unique]["lat"], 'long': geocache[entity_unique]["long"]}


def save_geocache():
    global geocache
    try:
        with open("geocache.json", "w", encoding="utf-8") as gc:
            json.dump(geocache, gc, ensure_ascii=False)
    except:
        pass


# create map of entities extracted from input file
# file_in_name - input file name
# lng - language of input file
def create_map(text="", lng="", doc=None, tmx=False):
    # dataframe of all entities in text
    entities_df = get_entities(text, lng, doc, tmx)
    # dataframe of entities with latitude, longitude and address
    loc_dfs = create_lat_lng(entities_df)
    if loc_dfs.empty:
        map = folium.Map(zoom_start=0,
                         control_scale=True)
    else:
        save_geocache()
        entities_with_lon_lat = pd.merge(entities_df, loc_dfs, on='entity')
        # create map for entities
        map = folium.Map(location=[entities_with_lon_lat.lat.mean(), entities_with_lon_lat.long.mean()], zoom_start=0,
                         control_scale=True)
        # add marker for entities on map
        for index, location_info in entities_with_lon_lat.iterrows():
            folium.Marker([location_info["lat"], location_info["long"]], popup=location_info['entity']).add_to(map)
    return map._repr_html_()



def fetch_name_and_definition_from_wikipedia(qid, lang='en'):

    title = ""
    summary = ""
    data = {}
    
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        try:
            summary = data['entities'][qid]['descriptions'][lang]['value']
        except:
            summary = ""
            try:
                title = data['entities'][qid]['sitelinks'].get(f'{lang}wiki', {}).get('title', '')
            except:
                pass
        if summary:
            return summary

    except:
        pass

    if title:
        summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            summary_response = requests.get(summary_url)
            summary_response.raise_for_status()  # Raise an exception for HTTP errors
            summary_data = summary_response.json()
            summary = summary_data.get('extract', "")
        except:
            pass

    return ""