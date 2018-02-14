import sys
import numpy as np

#open and read all files
textTuple = []
for i in range(1, 9):
    text = open("./Test Files/Doc " +  i.__str__() + ".txt", encoding="ISO_8859_1")
    textTuple.append(text.read())

stopWords = []

def checkWordCountInText(text, keyWord):
    splitUpText = text.split(" ")
    dictionaryOfWords = {}
    for word in splitUpText:
        if word in dictionaryOfWords:
            dictionaryOfWords[word] += 1
        else:
            dictionaryOfWords[word] = 1
    if keyWord in dictionaryOfWords:
        print("this is the number of keyword: " + keyWord + " =" + dictionaryOfWords[keyWord].__str__())

def countWords(allTexts, stopWords):
    wordCountMatrix = np.array([])
    wordArray = []
    textSizes = []
    for textInd in range(0, len(allTexts)):
        x = np.size(wordCountMatrix, -1)
        columnVec = np.zeros(x)
        #need preprocessing here!


        preprocessedText = allTexts[textInd].replace("\n", "").split(" ")
        textSizes.append(len(preprocessedText))
        for word in preprocessedText:
            if word not in stopWords:
                if word in wordArray:
                    columnVec[wordArray.index(word)] += 1
                else:
                    wordArray.append(word)
                    columnVec = np.append(columnVec, [1], axis=0)
        if np.size(wordCountMatrix, 0) != 0:
            wordCountMatrix = np.pad(wordCountMatrix, ((0,0),(0,columnVec.size - np.size(wordCountMatrix,1))), 'constant')
        else:
            wordCountMatrix.resize((textInd, columnVec.size))
        wordCountMatrix = np.concatenate((wordCountMatrix, [columnVec]), axis=0)
    return((wordArray, wordCountMatrix, textSizes))



def calcSentenceWeights(allTexts, wordArray, wordCountMatrix, textSizes):
    print(wordArray)
    sentenceWeightMatrix = np.array([])
    allSentences = []
    for textInd in range(0, len(allTexts)):
        sentencesInText = allTexts[textInd].split(".")
        allSentences.append(sentencesInText)
        sentenceWeights = np.zeros(len(sentencesInText))
        for sentenceInd in range(0, len(sentencesInText)):
            sentence = sentencesInText[sentenceInd]
            words = sentence.split(" ")
            for word in words:
                if word in wordArray:
                    # checkWordCountInText(allTexts[textInd], word)
                    # print(wordCountMatrix[textInd,wordArray.index(word)])
                    sentenceWeights[sentenceInd] += wordCountMatrix[textInd,wordArray.index(word)]
        if sentenceWeights.size >= np.size(sentenceWeightMatrix, -1):
            if np.size(sentenceWeightMatrix, 0)!= 0:
                sentenceWeightMatrix = np.pad(sentenceWeightMatrix, ((0,0),(0,sentenceWeights.size - np.size(sentenceWeightMatrix, 1))), 'constant')
            else:
                sentenceWeightMatrix.resize((textInd, sentenceWeights.size))
            sentenceWeightMatrix = np.concatenate((sentenceWeightMatrix, [sentenceWeights]), axis=0)
        else:
            sentenceWeights.resize(np.size(sentenceWeightMatrix, -1))
            sentenceWeightMatrix = np.concatenate((sentenceWeightMatrix, [sentenceWeights]), axis=0)
    # print(allSentences)
    print(sentenceWeightMatrix)


countedWords = countWords(textTuple, [])
listOfWords = countedWords[0]
wordCountMatr = countedWords[1]
docSizes = countedWords[2]
calcSentenceWeights(textTuple, listOfWords, wordCountMatr, docSizes)


