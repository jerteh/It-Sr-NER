import pandas as pd
import spacy
import flask
from flask import request, Response, render_template
from urllib.parse import unquote
import pathlib
import os


dir = str(pathlib.Path(__file__).parent.resolve())
conf = pd.read_csv(dir + "/config/lng_config.csv", delimiter='\t').set_index('lng')
tags = ['PERS', 'LOC', 'ORG', 'DEMO', 'EVENT', 'WORK']
nlps = {}


app = flask.Flask(__name__)
app.config["DEBUG"] = False


def process(req):
    query_parameters = req.form
    lang = query_parameters.get('lng')
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
    return data, lang, name


@app.route('/')
def home():
    return render_template('ui.html')


@app.route('/mono', methods=['POST'])
def mono():
    data, lng, name = process(request)
    return Response(monolingual_ner(data, lng), mimetype="text/plain",
                    headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


@app.route('/tmx', methods=['POST'])
def tmxd():
    data, lng, name = process(request)
    return Response(monolingual_ner(data, lng), mimetype="text/plain",
                    headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


# In input sentence (old), replace recognised NE with tagged NE (new):
# start, end are indexes of NE
def replace_string(old, new, start, end):
    first = old[:start]
    last = old[end:]
    return first + new + last


# apply NER and annotate with NER tags
def apply_NER_model_mono(text, nlp, lst_remove_tags):
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
    return marked_text


# tagset harmonisation: mapping NER labels to same tagset
def map_tags(marked_text, tags, lst_tags):
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
    global nlps
    global conf
    if lng not in nlps:
        nlps[lng] = load_model(lng)
    nlp = nlps[lng]
    lst_remove_tags = conf.loc[lng]['remove_types'].split(',')
    lst_tags = conf.loc[lng]['map_ner_types'].split(',')

    text_ner = apply_NER_model_mono(data, nlp, lst_remove_tags)
    harmonized_ner_text = map_tags(text_ner, tags, lst_tags)

    return harmonized_ner_text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
