import nltk
nltk.download('stopwords')

INDEX_NAME = "ptwiki" 
ES_HOST = "http://localhost:9200"
STOPWORDS = nltk.corpus.stopwords.words('portuguese')