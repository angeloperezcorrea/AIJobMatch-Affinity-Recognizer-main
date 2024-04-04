import joblib
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

def analize_speech(text):
    # print("Loading model and vectorizer...")
    model = joblib.load("models/modelo.pkl")
    vectorizer = joblib.load("models/vectorizador.pkl")

    stemmer = SnowballStemmer("spanish")
    # print("Preprocessing text...")
    def tokenize_and_stem(text):
        tokens = word_tokenize(text.lower())
        stems = [stemmer.stem(token) for token in tokens if token.isalpha()]
        return ' '.join(stems)


    # with open("data/Graciela/Graciela.txt", "r") as archivo:
    #     text = archivo.read()
        
    text_preprocessed = tokenize_and_stem(text)
    text_transformed = vectorizer.transform([text_preprocessed])

    # print("Predicting...")
    prediction = model.predict(text_transformed)

    return str(prediction[0])