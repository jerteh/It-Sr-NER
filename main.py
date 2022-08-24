import pandas as pd
import spacy


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


def monolingual_ner(data, lng):
    global nlps
    global conf
    if lng not in nlps:
        mname = conf.loc[lng]['lng_model']
        try:
            nlps[lng] = spacy.load(mname)
        except:
            nlps[lng] = spacy.load("models\\"+mname)
    nlp = nlps[lng]
    lst_remove_tags = conf.loc[lng]['remove_types'].split(',')
    lst_tags = conf.loc[lng]['map_ner_types'].split(',')

    # file_name = "It-Sr-NER/" + lng + "/" + f_name
    # with open(file_name, 'r', encoding='utf-8') as fid:
    #    data = fid.read()

    # apply model and harmonise tagset
    text_ner = apply_NER_model_mono(data, nlp, lst_remove_tags)
    harmonized_ner_text = map_tags(text_ner, tags, lst_tags)

    # write temp file - ovo može da bude i preskočeno, ali za testiranje potrebno
    # f_tmp_name = file_name.replace(".txt", "-ner.txt")
    # f_tmp = open(f_tmp_name, 'w', encoding='utf-8')
    # f_tmp.write(text_ner)
    # f_tmp.close()

    # write out file
    # f_out_name = file_name.replace(".txt", "-6ner.xml")
    # f_out = open(f_out_name, 'w', encoding='utf-8')
    # f_out.write('<div>\n' + harmonized_ner_text + '\n</div>')
    # f_out.close()
    print(harmonized_ner_text)


conf = pd.read_csv("./config/lng_config.csv", delimiter='\t').set_index('lng')
tags = ['PERS', 'LOC', 'ORG', 'DEMO', 'EVENT', 'WORK']
nlps = {}
monolingual_ner("Zdravo, ja se zovem Miloš i dolazim iz Požarevca.", "en")
