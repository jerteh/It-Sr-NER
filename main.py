import flask
from flask import request, Response, render_template, make_response
from urllib.parse import unquote
import os

from spacyworks import monolingual_ner_nel, bilingual_ner_nel, languages


app = flask.Flask(__name__)
app.config["DEBUG"] = False


def process_mono(req):
    query_parameters = req.form
    if "file" in req.files:
        text = False
        file = req.files["file"]
        if file.filename != "":
            data = file.read().decode("utf-8")
            name = file.filename
        else:
            text = True
            data = query_parameters.get('data')
            data = unquote(data)
            name = "results"
    else:
        text = True
        data = query_parameters.get('data')
        data = unquote(data)
        name = "results"

    lang = query_parameters.get('lng')
    w_nel = query_parameters.get('with_nel')
    if w_nel == "on":
        with_nel = True
    else:
        with_nel = False

    w_ner = query_parameters.get('with_ner')
    if w_ner == "on":
        with_ner = True
    else:
        with_ner = False

    return data, lang, name, with_nel, with_ner, text


def process_tmx(req):
    file = req.files["file"]
    query_parameters = req.form
    if file.filename != "":
        name = file.filename
    else:
        name = "results"

    w_nel = query_parameters.get('with_nel')
    if w_nel == "on":
        with_nel = True
    else:
        with_nel = False

    w_ner = query_parameters.get('with_ner')
    if w_ner == "on":
        with_ner = True
    else:
        with_ner = False

    return file, name, with_nel, with_ner


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


@app.route('/mono', methods=['POST'])
def mono():
    data, lng, name, with_nel, with_ner, text = process_mono(request)
    if text:
        template = render_template('string.html', data=monolingual_ner_nel(data, lng, with_ner, with_nel))
        response = make_response(template)
        response.headers['Content-Type'] = 'application/xml'
        return response
    else:
        return Response(monolingual_ner_nel(data, lng, with_ner, with_nel), mimetype="text/plain",
                        headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


@app.route('/tmx', methods=['POST'])
def tmxd():
    file, name, with_nel, with_ner = process_tmx(request)
    return Response(bilingual_ner_nel(file, with_ner, with_nel), mimetype="text/plain",
                    headers={'Content-Disposition': 'attachment;filename=' + name + '.ner'})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
