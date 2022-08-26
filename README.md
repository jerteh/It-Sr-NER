# It-Sr-NER
Project: "It-Sr-NER: CLARIN compatible NER and geoparsing web services for parallel texts: case study Italian and Serbian " 
Call "Bridging Gaps - A Call for Expressions of Interest to Connect CLARIN to External Language Technology Tools" 2022
Project duration: 1.6.2022-30.9.2022.
Project leader: Olja Perišić, Università degli Studi di Torino, Dipartimento di Lingue e Letterature Straniere e Culture Moderne, Italy
Project members are from Jerteh  - Society for Language Resources and Tools, Serbia Duško Vitas, Ranka Stanković, Milica Ikonić Nešić
Contributors also: Cvetana Krstev, Saša Moderc, Mihailo Škorić. 
Main goal: development of the CLARIN compatible NER web service for parallel text with case study on Italian and Serbian, dubbed It-Sr-NER. Service could be used for recognizing and classifying named entities in bilingual natural language texts. Input would be parallel texts expected to be TMX (Translation Memory eXchange) file, e.g. Sr-It. It-Sr-NER would recognize six NER classes: demonyms (DEMO), works of art (WORK), person names (PERS), places (LOC), events (EVENT) and organisations (ORG). Although primarily developed for aligned, parallel texts in TMX, the use of the service for monolingual text NER annotation for available spaCy NER models will be possible. It-Sr-NER uses a powerful Convolutional Neural Network architecture within the spaCy tool.

# API usage instructions

### URL:
  
hostname/mono for monolingual NER annotation

OR

hostname/tmx for bilingual NER annotation of TMX files

### required keys should be form-posted:
  
   lng: language code [text]
	 
   AND
	 
   file: file that shpuld be processed [file]
	 
   OR
	 
   data: string that should be processed [txt]
  
