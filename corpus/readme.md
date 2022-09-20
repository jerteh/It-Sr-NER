# Italian-Serbian aligned corpus: It-Sr-NER-corp

 It-Sr-NER-corp is the Italian/Serbian bilingual corpus with 10,000 aligned sentences compiled in the scope of the It-Sr-project from samples of several Italian novels translated to Serbian and vice versa,  with the aim of the development of the CLARIN compatible NER web service for parallel text with the case study on Italian and Serbian. The set of 10,000 natural language segments is split into 4 files: 1x1000+3x3000. 
 
Automatic annotation of named entities is performed for six NER classes: demonyms (DEMO), works of art (WORK), person names (PERS), places (LOC), events (EVENT) and organizations (ORG). It-Sr-NER annotation uses a powerful Convolutional Neural Network architecture within the spaCy tool, for Italien WikiNER (Joel Nothman, Nicky Ringland, Will Radford, Tara Murphy, James R Curran) and for Serbian SrpCNNER (Cvetana Krstev, Ranka Stanković, Milica Ikonić Nešić, Branislava Šandrih Todorović).
 
 The corpus *It-Sr-NER-corp*  comprises of: 
 1) monolingual, with one segment per line 
 - It-txt: Italian text files
 - It-txt-NER: NER annotated Italian files
 - It-txt-NER-NEL: NER annotated Italian files with links to Wikidata
 - It-txt-NEL: Entity linking in Italian files using only [spaCyOpenTapioca](https://github.com/UB-Mannheim/spacyopentapioca#spacyopentapioca)
 - Sr-txt: Serbian text files
 - Sr-txt-NER: NER annotated Serbian files
 - Sr-txt-NER-NEL: NER annotated Serbian files with links to Wikidata
 - Sr-txt-NEL: Entity linking in Serbian files using only [spaCyOpenTapioca](https://github.com/UB-Mannheim/spacyopentapioca#spacyopentapioca)
 2) bilingual aligned segments: 
 - It-Sr-html: html version of aligned segments
 - It-Sr-tmx: xml files with TMX (Translation Memory eXchange) 
 - It-Sr-tmx-NER: TXM files with annoted named entities
 - It-Sr-tmx-NER-NEL: NER annotated TMX files with links to Wikidata
 - It-Sr-tmx-NEL: Entity linking in TMX files using only [spaCyOpenTapioca](https://github.com/UB-Mannheim/spacyopentapioca#spacyopentapioca) 
 
**Authors**: Perisic Olja, Vitas Duško, Krstev Cvetana, Moderc Saša, Stanković Ranka  
**NER and NEL annotation**: Milica Ikonić Nešić, **Web service**: Mihailo Škorić

**Publisher**: Università degli Studi di Torino, Dipartimento di Lingue e Letterature Straniere e Culture Moderne, Italy
**Contact person**: Perisic Olja, olja.perisic@unito.it, Università degli Studi di Torino, Dipartimento di Lingue e Letterature Straniere e Culture Moderne, Italy
**Funding**: CLARIN ERIC , Project title: *It-Sr-NER: CLARIN compatible NER and geoparsing web services for parallel texts: case study Italian and Serbian*, grantNo:  *CE-2022-2070*, funding type: *CLARIN Bridging Gaps project*.

**License**: CC-BY-4.0

# Annotation examples
It-Sr-tmx-NER: TXM files with annoted named entities

```
<tu>  
   <prop type="Domain"/>  			
   <tuv xml:lang="it" creationid="n54" creationdate="20220825T211907Z">  			
      <seg>Progettava di raggiungere <LOC>Parigi</LOC> insieme ad altri suoi compagni, mi invitò ad andare con lei in automobile.</seg>  
   </tuv>  
   <tuv xml:lang="sr" creationid="n54" creationdate="20220825T211907Z">  
      <seg>Plan joj je bio da stigne u <LOC>Pariz</LOC> zajedno sa drugim svojim kolegama, pozvala me je da joj se pridružim, išle bismo automobilom.</seg>  
   </tuv>  			
</tu>  
```
It-Sr-tmx-NER-NEL: TXM files with annoted named entities and Wikidata named entity linking

```
<tu>  
   <prop type="Domain"/>  			
   <tuv xml:lang="it" creationid="n54" creationdate="20220825T211907Z">  			
      <seg>Progettava di raggiungere <LOC ref="https://www.wikidata.org/wiki/Q90" desc="capital and largest city of France">Parigi</LOC> insieme ad altri suoi compagni, mi invitò ad andare con lei in automobile.</seg>  
   </tuv>  
   <tuv xml:lang="sr" creationid="n54" creationdate="20220825T211907Z">  
      <seg>Plan joj je bio da stigne u <LOC ref="https://www.wikidata.org/wiki/Q90" desc="capital and largest city of France">Pariz</LOC> zajedno sa drugim svojim kolegama, pozvala me je da joj se pridružim, išle bismo automobilom.</seg>  
   </tuv>  			
</tu>  
```
It-Sr-tmx-NEL: TXM files with annoted Wikidata named entity linking

```
<tu>  
   <prop type="Domain"/>  			
   <tuv xml:lang="it" creationid="n54" creationdate="20220825T211907Z">  			
      <seg>Progettava di raggiungere <LOC>Parigi</LOC> insieme ad altri suoi compagni, mi invitò ad andare con lei in automobile.</seg>  
   </tuv>  
   <tuv xml:lang="sr" creationid="n54" creationdate="20220825T211907Z">  
      <seg>Plan joj je bio da stigne u <LOC>Pariz</LOC> zajedno sa drugim svojim kolegama, pozvala me je da joj se pridružim, išle bismo automobilom.</seg>  
   </tuv>  			
</tu>  
```
