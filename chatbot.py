import random 
import json
import pickle 
import numpy as np
import nltk
from flask import Flask , render_template, request, jsonify
from flask_cors import CORS
import difflib
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
models = genai.list_models()
for m in models:
    if "generateContent" in m.supported_generation_methods:
        print(m.name)

app=Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Super sercret key'

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json', encoding="utf-8").read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

model = load_model('chatbot_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words 

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag=[0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i]=1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i, r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key = lambda x:x[1], reverse = True)
    return_list =[]
    for r in results:
        return_list.append({'intent':classes[r[0]], 'probability':str(r[1])})
    return return_list

# def get_response(intents_list, intents_json):
#     list_of_intents = intents_json['intents']
#     tag = intents_list[0]['intent']
#     for i in list_of_intents:
#         if i['tag'] == tag:
#             result = random.choice(i['responses'])
#             break
    
#     return result


def get_response(intents_list, intents_json, user_input):
    list_of_intents = intents_json['intents']
    tag = intents_list[0]['intent']

    for intent in list_of_intents:
        if intent['tag'] == tag:
            best_match = difflib.get_close_matches(user_input.lower(), intent['patterns'], n=1, cutoff=0.5)
            if best_match:
                index = intent['patterns'].index(best_match[0])
                return intent['responses'][index % len(intent['responses'])]  # match index to response
            else:
                return random.choice(intent['responses'])


print("Great! Bot is Running!")

@app.route("/")
def home():
    return render_template("home.html") 

@app.route('/chat',methods = ['POST' , 'GET'])
def chat():
    msg = request.get_json()
    if not msg or 'message' not in msg:
        return jsonify({"error": "Invalid input"}), 400
    
    user_message = msg['message'] 
    
    ints = predict_class(user_message)
    confidence = float(ints[0]['probability'])
    
    if confidence > 0.70:
        res = get_response(ints, intents, user_message )
        print("data")
    else:
        print("gemini")
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(user_message)
        res = response.text
    # res = get_response(ints, intents, user_message)
    return jsonify({"response" : res})

if __name__ == "__main__":
    app.run(debug=True)


# while True:
#     message = input("")
#     ints = predict_class(message)
#     res = get_response(ints, intents)
#     print(res)
            