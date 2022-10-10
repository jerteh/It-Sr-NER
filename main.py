import flask
from flask import request, Response, render_template, make_response
from urllib.parse import unquote
import os
import re
import requests

from spacyworks import monolingual_ner_nel, bilingual_ner_nel, languages, create_map

app = flask.Flask(__name__)
app.config["DEBUG"] = False


def isurl(string):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, string) is not None


def process_text(data):
    data = unquote(data)
    if isurl(data):
        data = requests.get(data).text
    return data, True, "results"


def process_req(req):
    query_parameters = req.args
    if len(query_parameters) == 0:
        query_parameters = req.form
        thedata = query_parameters.get('data')
    else:
        thedata = query_parameters["data"]
    lang = query_parameters.get('lng')
    feat = query_parameters.get('feat')
    tmx = False

    if "file" in req.files:
        text = False
        file = req.files["file"]
        if file.filename != "":
            data = file.read().decode("utf-8")
            name = file.filename
            if ".tmx" in name:
                tmx = True
            return data, lang, name, feat, text, tmx

    data, text, name = process_text(thedata)
    return data, lang, name, feat, text, tmx


@app.route('/')
def home():
    return render_template('ui.html', data=languages)


@app.route('/example.tmx')
def example():
    template = render_template('example.tmx')
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/img')
def img():
    return render_template('img.html', data=os.path.join('static', 'It-Sr-NER.png'))


@app.route('/4api')
def api():
    return render_template('api.html', data=request.root_url)


@app.route('/api', methods=['POST', 'GET'])
def serv():
    data, lng, name, feat, text, tmx = process_req(request)

    if feat == "geo":
        return Response(create_map(text=data, lng=lng, tmx=tmx))

    else:
        ner = False
        nel = False

        if "ner" in feat:
            ner = True
        if "nel" in feat:
            nel = True

        if text:
            template = render_template('string.html', data=monolingual_ner_nel(data, lng, ner, nel))
            response = make_response(template)
            response.headers['Content-Type'] = 'application/xml'
            return response
        else:
            if tmx:
                resp = bilingual_ner_nel(data, ner, nel)
            else:
                resp = monolingual_ner_nel(data, lng, ner, nel)

            return Response(resp, mimetype="text/plain",
                            headers={'Content-Disposition': 'attachment;filename=' + name[0:-4]
                                                            + ('-ner' if ner else '')
                                                            + ('-nel' if nel else '') + name[-4:]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
