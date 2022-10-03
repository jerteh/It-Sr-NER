import flask
from flask import request, Response, render_template, make_response
from urllib.parse import unquote
import os

from spacyworks import monolingual_ner_nel, bilingual_ner_nel, languages, create_map

app = flask.Flask(__name__)
app.config["DEBUG"] = False


def process_req(req):
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
    w_ner = query_parameters.get('with_ner')
    w_tmx = query_parameters.get('with_tmx')
    w_map = query_parameters.get('with_map')

    with_nel = w_nel == "on"
    tmx = w_tmx == "on"
    with_ner = w_ner == "on"

    return data, lang, name, with_nel, with_ner, text, tmx


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


@app.route('/mapi', methods=['POST'])
def mapi():
    data, lng, name, with_nel, with_ner, text, tmx = process_req(request)
    map = create_map(text=data, lng=lng, tmx=tmx)
    return Response(map)


@app.route('/api', methods=['POST'])
def serv():
    data, lng, name, with_nel, with_ner, text, tmx = process_req(request)

    if text:
        template = render_template('string.html', data=monolingual_ner_nel(data, lng, with_ner, with_nel))
        response = make_response(template)
        response.headers['Content-Type'] = 'application/xml'
        return response
    else:
        if tmx:
            resp = bilingual_ner_nel(data, with_ner, with_nel)
        else:
            resp = monolingual_ner_nel(data, lng, with_ner, with_nel)

        return Response(resp, mimetype="text/plain",
                        headers={'Content-Disposition': 'attachment;filename=' + name[0:-4]
                                                        + ('-ner' if with_ner else '')
                                                        + ('-nel' if with_nel else '') + name[-4:]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
