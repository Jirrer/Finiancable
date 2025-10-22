from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib, csv
from typing import List, Tuple
from ParsePDFs import parsePdf


def RunLLM(strings: list) -> list:
    vectorizer = joblib.load("LLM_data\\vectorizer.joblib")

    clf = joblib.load("LLM_data\\classifier.joblib")

    predictions = clf.predict(vectorizer.transform(strings))
    
    return predictions

def TrainModel():
    texts, labels = [], []

    purchasesArray = parsePdf(['LLM_data\\TrainingData.PDF'])

    for purchase in purchasesArray:
        texts.append(purchase)
        labels.append(input(f"{purchase}: "))

    newModel = (texts, labels)

    TrainLLM(newModel)

def TrainLLM(newModel: Tuple[List[str], List[str]]):
    oldText, oldLabels = pullFromCsv('LLM_data\\Texts.csv'), pullFromCsv('LLM_data\\Labels.csv')

    newText, newLabels = newModel[0], newModel[1]

    if len(newText) != len(newLabels):
        print("Number of Labels does not match number of texts!")
        return

    oldText.extend(newText)
    oldLabels.extend(newLabels)

    finalText, finalLabels = oldText, oldLabels

    if finalText and finalLabels:
        pushToCsv('LLM_data\\Texts.csv', finalText)
        pushToCsv('LLM_data\\Labels.csv',finalLabels)

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(finalText)

        clf = MultinomialNB()
        clf.fit(X, finalLabels)

        joblib.dump(vectorizer,"LLM_data\\vectorizer.joblib")
        joblib.dump(clf, "LLM_data\\classifier.joblib")

        print("Model trained and saved successfully!")
    else:
        joblib.dump('',"LLM_data\\vectorizer.joblib")
        joblib.dump('', "LLM_data\\classifier.joblib")
        print("Empty Model")

def ClearLLM():
    with open('LLM_data\\Texts.csv', mode='w', newline='') as file: pass
    with open('LLM_data\\Labels.csv', mode='w', newline='') as file: pass

    TrainLLM(([], []))

def pullFromCsv(fileLocation):
    output = []
    
    with open(fileLocation, mode='r', newline='') as file:
        reader = csv.reader(file)

        for row in reader:
            if row: output.append(row[0])

    return output

def pushToCsv(fileLocation, content: list):
    with open(fileLocation, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(content)
