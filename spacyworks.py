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
for lng in languages:
    dic_remove_tags[lng] = conf.loc[lng]['remove_types'].split(',')
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


def tapioca_nel(text):
    # general nlp object for nle using opentapioca
    nlp_nel = spacy.blank('en')
    nlp_nel.add_pipe('opentapioca')
    # split text into chunks with max 300 lines of text
    chunks = text_chunks(text, 300)
    # create list of tuples with entities text and list of QID and descriptions in wikidata - new function
    # tuple: (Beograd, [Q371, 'City in Serbia'])
    text_qid_desc = []
    for chunk in chunks:
        text = '\n'.join(chunk)
        #  doc object with applied nlp_nel on input text
        doc_nel = nlp_nel(text)
        for ent_nel in doc_nel.ents:
            text_qid_desc.append((ent_nel.text, list((ent_nel.kb_id_, ent_nel._.description))))
    # crete dictionary
    Dict = dict(text_qid_desc)
    return Dict


def apply_NEL_model_mono(text):
    nlp = spacy.blank('en')
    # add in pipe opentapioca
    nlp.add_pipe('opentapioca')
    marked_text = text
    text_ner = ''
    chunks = text_chunks(marked_text, 300)
    for chunk in chunks:
        move_p = 0
        text_chunk = '\n'.join(chunk)
        # apply NEL model to input text
        doc = nlp(text_chunk)
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
        text_ner = text_ner + text_chunk + '\n'
    return text_ner


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


def monolingual_ner_nel(data, lng, with_ner, with_nel,):

    if with_nel and with_ner:
        return apply_NER_NEL_model_mono(data, lng)
    else:
        if with_ner:
            return apply_NER_model_mono(data, lng)
        if with_nel:
            return apply_NEL_model_mono(data)


def bilingual_ner_nel(file, with_ner, with_nel):
    try:
        el = etree.parse(file)
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
    except:
        return "Submited file was not properly formatted :(("

