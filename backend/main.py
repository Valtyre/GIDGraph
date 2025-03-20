from nlp.spacy_test import nlp_runner
import json

if __name__ == '__main__':
    with open("backend/nlp/nl_texts.json", "r") as file:
        data = json.load(file)
    
    print(nlp_runner(data["text1"]))