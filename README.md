# It-Sr-NER
It-Sr-NER: CLARIN compatible NER and geoparsing web services  for Italian and Serbian parallel text

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
  
