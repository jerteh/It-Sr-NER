import spacy
import os
import pathlib
from helper import text_chunks, replace_string
from lxml import etree
import pandas as pd
import numpy as np


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
# tapioca NEL
nlp_nel = spacy.blank('en')
# for local
# nlp_nel.add_pipe('opentapioca', config={"url": OpenTapiocaAPI})
nlp_nel.add_pipe('opentapioca')

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
            x = spacy.load(dir_x + "/models/" + mname + "/" + os.listdir(dir_x + "/models/" + mname)[0])
    return x


# user for NER+NEL
def tapioca_nel(text):
    # create list of tuples with entities text and list of QID and descriptions in wikidata - new function
    # tuple: (Beograd, [Q371, 'City in Serbia'])
    text_qid_desc = []
    if (len(text) < text_size_without_chunking):
        doc_nel = nlp_nel(text)
        for ent_nel in doc_nel.ents:
            text_qid_desc.append((ent_nel.text, list((ent_nel.kb_id_, ent_nel._.description))))
    else:
        # split text into chunks with max chunk_size (= 300) lines of text
        chunks = text_chunks(text, chunk_size)
        for chunk in chunks:
            text_chunk = '\n'.join(chunk)
            #  doc object with applied nlp_nel on input text
            doc_nel = nlp_nel(text_chunk)
            for ent_nel in doc_nel.ents:
                text_qid_desc.append((ent_nel.text, list((ent_nel.kb_id_, ent_nel._.description))))
    # crete dictionary
    dict_ent = dict(text_qid_desc)
    return dict_ent


# optimizovati
def apply_NEL_model_mono(text):
    marked_text = text

    if (len(text)<text_size_without_chunking ):
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
    doc = nlp_nel(text_chunk)
    for ent in doc.ents:
        # create link with QID of entity
        QID = "https://www.wikidata.org/wiki/" + ent.kb_id_
        # entity description
        Desc = ent._.description
        # start position of entity after adding labels
        start = move_p + ent.start_char
        # end position of entity after adding labels
        end = move_p + ent.end_char
        new = '<WDT ref="' + QID + '"' + ' label="' + ent.label_ + '" desc="' + str(
            Desc) + '"' + '>' + ent.text + '</WDT>'
        text_chunk = replace_string(text_chunk, new, start, end)
        # add two lenghts for labels and five for <></>
        up = int(len(QID) + len(str(Desc)) + 35 + len(ent.label_))
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
    Dict = tapioca_nel(text)
    # move position
    move_p = 0
    marked_text = text
    for ent in doc.ents:
        if ent.label_ not in lst_remove_tags:
            # start position of entity after adding labels
            start = move_p + ent.start_char
            # end position of entity after adding labels
            end = move_p + ent.end_char
            # if entity text is in dictionary
            if ent.text in Dict.keys():
                # get qid from dictionary Dict for entity
                QID = "https://www.wikidata.org/wiki/" + Dict.get(ent.text)[0]
                # get desccription from dictionary Dict_desc for entity
                Desc = Dict.get(ent.text)[1]
                new = '<' + ent.label_ + ' ref="' + QID + '"' + ' desc="' + str(
                    Desc) + '"''>' + ent.text + '</' + ent.label_ + '>'
                marked_text = replace_string(marked_text, new, start, end)
                # add two lenghts for labels and five for <></>
                up = int(2 * len(ent.label_) + 5 + len(QID) + len(str(Desc)) + 15)
            else:
                new = '<' + ent.label_ + '>' + ent.text + '</' + ent.label_ + '>'
                marked_text = replace_string(marked_text, new, start, end)
                # add two lenghts for labels and five for <></>
                up = int(2 * len(ent.label_) + 5)
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
            # start position of entity after adding labels
            start = move_p + ent.start_char
            # end position of entity after adding labels
            end = move_p + ent.end_char
            new = '<' + ent.label_ + '>' + ent.text + '</' + ent.label_ + '>'
            marked_text = replace_string(marked_text, new, start, end)
            # add two lenghts for labels and five for <></>
            up = int(2 * len(ent.label_) + 5)
            move_p += up
    marked_text = map_tags(marked_text, lng)
    return marked_text


def monolingual_ner_nel(data, lng, with_ner=True, with_nel=False):

    if with_nel and with_ner:
        return apply_NER_NEL_model_mono(data, lng)
    elif with_nel:
        return apply_NEL_model_mono(data)
    elif with_ner:
        return apply_NER_model_mono(data, lng)
    else:
        return data


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
    #except:
     #   return "Submited file was not properly formatted :(("

