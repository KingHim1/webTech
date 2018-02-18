import sys
import numpy as np

#open and read all files
textTuple = []
for i in range(1, 9):
    text = open("./Test Files/Doc " +  i.__str__() + ".txt", encoding="ISO_8859_1")
    textTuple.append(text.read())

stopWords = ["and", "the", "then", "so", "if", "him", "a", "an", "be", "for", "from", "in", "with"]

summaryFile = open("./tf_summary.txt", "w")

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

        preprocessedText = allTexts[textInd].replace("\n", "").replace("\"", "").replace("\n\n", "").split(" ")
        textSizes.append(len(preprocessedText))
        for word in preprocessedText:
            if word not in stopWords:
                if word in wordArray:
                    columnVec[wordArray.index(word)] += 1
                else:
                    wordArray.append(word)
                    columnVec = np.append(columnVec, [1], axis=0)
        columnVec /= textSizes[textInd]
        if np.size(wordCountMatrix, 0) != 0:
            wordCountMatrix = np.pad(wordCountMatrix, ((0,0),(0,columnVec.size - np.size(wordCountMatrix,1))), 'constant')
        else:
            wordCountMatrix.resize((textInd, columnVec.size))
        wordCountMatrix = np.concatenate((wordCountMatrix, [columnVec]), axis=0)
    return((wordArray, wordCountMatrix, textSizes))



def calcSentenceWeights(allTexts, wordArray, wordCountMatrix, textSizes):
    sentenceWeightMatrix = np.array([])
    allSentences = []
    for textInd in range(0, len(allTexts)):
        sentencesInText = allTexts[textInd].split(".")
        allSentences.append(sentencesInText)
        sentenceWeights = np.zeros(len(sentencesInText))
        for sentenceInd in range(0, len(sentencesInText)):
            sentenceStructureOffset = (-1 / 2) * ((sentenceInd) / len(sentencesInText)) + 1
            sentence = sentencesInText[sentenceInd]
            words = sentence.split(" ")
            for word in words:
                if word in wordArray:
                    sentenceWeights[sentenceInd] += wordCountMatrix[textInd,wordArray.index(word)]
            sentenceWeights[sentenceInd] *= sentenceStructureOffset
        if sentenceWeights.size >= np.size(sentenceWeightMatrix, -1):
            if np.size(sentenceWeightMatrix, 0)!= 0:
                sentenceWeightMatrix = np.pad(sentenceWeightMatrix, ((0,0),(0,sentenceWeights.size - np.size(sentenceWeightMatrix, 1))), 'constant')
            else:
                sentenceWeightMatrix.resize((textInd, sentenceWeights.size))
            sentenceWeightMatrix = np.concatenate((sentenceWeightMatrix, [sentenceWeights]), axis=0)
        else:
            sentenceWeights.resize(np.size(sentenceWeightMatrix, -1))
            sentenceWeightMatrix = np.concatenate((sentenceWeightMatrix, [sentenceWeights]), axis=0)
    return(sentenceWeightMatrix, allSentences)
    # print(allSentences)
    print(sentenceWeightMatrix)

def isSentenceSimilar(sentence1, sentence2):
    sentence1 = sentence1.split(" ")
    sentence2 = sentence2.split(" ")
    count = 0
    for word in sentence2:
        if word in sentence1:
            count += 1
    if count/len(sentence2) > 0.6:
        return True


def summarise(allTexts, stopWords, summaryLength):
    countedWords = countWords(textTuple, stopWords)
    listOfWords = countedWords[0]
    wordCountMatr = countedWords[1]
    docSizes = countedWords[2]
    sentenceWeightsAndSentences = calcSentenceWeights(textTuple, listOfWords, wordCountMatr, docSizes)
    sentenceWeightMatrix = sentenceWeightsAndSentences[0]
    sentences = sentenceWeightsAndSentences[1]
    summary = []
    lengthCheckList = []
    while (len(summary) != 8 or lengthCheckList.count(True) != len(lengthCheckList)):
        for x in range(0, 8):
            bestSentence = (sentences[x][np.argmax(sentenceWeightMatrix[x])])
            sentences[x].remove(bestSentence)
            allTexts[x] = ".".join(sentences[x])
            lenOfBestSentence = len(bestSentence.split(" "))
            if len(summary) != 8 and lenOfBestSentence <= summaryLength:
                summary.append(bestSentence)
                lengthCheckList.append(False)
            elif (lenOfBestSentence + len(summary[x].split(" ")) <= summaryLength) and lenOfBestSentence != 0:
                if not isSentenceSimilar(summary[x], bestSentence):
                    summary[x] = summary[x] + bestSentence
            elif (lenOfBestSentence + len(summary[x].split(" ")) > summaryLength):
                # find second sentence with suitable length
                count = 0
                maxSentenceValue = 0
                for sentenceIndex in range(0, len(sentences[x])):
                    count += 1
                    if len(sentences[x][sentenceIndex].split(" ")) + len(summary[x].split(" ")) <= summaryLength:
                        if sentenceWeightMatrix[x][sentenceIndex] > maxSentenceValue:
                            maxSentenceValue = sentenceWeightMatrix[x][sentenceIndex]
                            bestSentence = sentences[x][sentenceIndex]
                if len(bestSentence.split(" ")) + len(summary[x].split(" ")) <= summaryLength:
                    if isSentenceSimilar(summary[x], bestSentence):
                        summary[x] = summary[x] +  bestSentence
                if count == len(sentences[x]):
                    lengthCheckList[x] = True
                if bestSentence in sentences[x]:
                    sentences[x].remove(bestSentence)
                    allTexts[x] = ".".join(sentences[x])
        countedWords = countWords(allTexts, stopWords)
        listOfWords = countedWords[0]
        wordCountMatr = countedWords[1]
        docSizes = countedWords[2]
        sentenceWeightsAndSentences = calcSentenceWeights(textTuple, listOfWords, wordCountMatr, docSizes)
        sentenceWeightMatrix = sentenceWeightsAndSentences[0]
        sentences = sentenceWeightsAndSentences[1]
    for summaryText in summary:
        print(len(summaryText.split(" ")))
        summaryFile.write(summaryText + "\n ---------------------------------------- \n")

summarise(textTuple, ["and", "the", "then", "so", "if", "him", "a", "an", "be", "for", "from", "in", "with"], 150)