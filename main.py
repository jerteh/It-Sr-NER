import pandas as pd
import spacy
import flask
from flask import request, Response, render_template, make_response
from urllib.parse import unquote
import pathlib
import os
from lxml import etree
import numpy as np


dir = str(pathlib.Path(__file__).parent.resolve())
conf = pd.read_csv(dir + "/config/lng_config.csv", delimiter='\t').set_index('lng')
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


app = flask.Flask(__name__)
app.config["DEBUG"] = False


def process_mono(req):
    query_parameters = req.form
    if "file" in req.files:
        file = req.files["file"]
        if file.filename != "":
            data = file.read().decode("utf-8")
            name = file.filename
        else:
            data = query_parameters.get('data')
            data = unquote(data)
            name = "results"
    else:
        data = query_parameters.get('data')
        data = unquote(data)
        name = "results"

    lang = query_parameters.get('lng')
    return data, lang, name


def process_tmx(req):
    file = req.files["file"]
    if file.filename != "":
        name = file.filename
    else:
        name = "results"

    return file, name


@app.route('/')
def home():
    return render_template('ui.html', data=languages)


@app.route('/example.tmx')
def example():
    template = render_template('example.tmx')
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/4api')
def api():
    return render_template('api.html', data=request.root_url)


@app.route('/mono', methods=['POST'])
def mono():
    data, lng, name = process_mono(request)
    return Response(monolingual_ner(data, lng), mimetype="text/plain",
                    headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


@app.route('/tmx', methods=['POST'])
def tmxd():
    file, name = process_tmx(request)
    return Response(bilingual_ner(file), mimetype="text/plain",
                    headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


# In input sentence (old), replace recognised NE with tagged NE (new):
# start, end are indexes of NE
def replace_string(old, new, start, end):
    first = old[:start]
    last = old[end:]
    return first + new + last


# apply NER and annotate with NER tags
def apply_NER_model_mono(text, lng):
    global nlps
    if lng not in nlps:
        nlps[lng] = load_model(lng)
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


# tagset harmonisation: mapping NER labels to same tagset
def map_tags(marked_text, lng):
    lst_tags = dic_tags[lng]
    i = 0
    f = marked_text
    for ne_tags in lst_tags:
        for tag in ne_tags.split('+'):
            if tag != tags[i] and tag != '':
                f = f.replace("<" + tag + ">", "<" + tags[i] + ">")
                f = f.replace("</" + tag + ">", "</" + tags[i] + ">")
        i += 1
    return f


def load_model(lng):
    mname = conf.loc[lng, 'lng_model']
    try:
        x = spacy.load(mname).from_disk(dir + "/models/" + mname)
    except:
        try:
            x = spacy.load(dir + "/models/" + mname)
        except:
            x = spacy.load(dir + "/models/" + mname + "/" + os.listdir(dir + "/models/" + mname)[0])
    return x


def monolingual_ner(data, lng):
    try:
        return apply_NER_model_mono(data, lng)
    except:
        return "Submited string or file was not properly formatted :(("


def bilingual_ner(file):
    try:
        el = etree.parse(file)
        tus = el.xpath("//*[local-name()='tu']")
        for tu in tus:
            tuvs = tu.xpath("*[local-name()='tuv']")
            for tuv in tuvs:
                lng = tuv.xpath("./@xml:lang", namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})[0]
                data = tuv.getchildren()[0].text  # tuv/seg
                # apply model and harmonise tagset
                text_ner = apply_NER_model_mono(data, lng)
                tuv.getchildren()[0].text = text_ner  # ažurirati tuv/seg sadržaj

        # read xml as string
        xml_str = etree.tostring(el, encoding='unicode')
        # replace special characters
        xml_str = xml_str.replace("&gt;", ">").replace("&lt;", "<")
        return xml_str

    except:
        return "Submited file was not properly formatted :(("


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
