import sys
import numpy as np

#open and read all files
textTuple = []
for i in range(1, 9):
    text = open("./Test Files/Doc " +  i.__str__() + ".txt", encoding="ISO_8859_1")
    textTuple.append(text.read())

summaryFile = open("./tfidf_summary.txt", "w")

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

def numOfFilesWithWord(word, listsOfWordsInTexts):
    count = 0
    for listOfWords in listsOfWordsInTexts:
        if word in listOfWords:
            count += 1
    return count


def countWords(allTexts):
    wordCountMatrix = np.array([])
    wordArray = []
    textSizes = []
    idfValues = []
    preprocessedTexts = []
    for i in range(0, len(allTexts)):
        preprocessedTexts.append(allTexts[i].replace("\n", "").replace("\"", "").replace("\n\n", "").split(" "))
        textSizes.append(len(preprocessedTexts[i]))
    for textInd in range(0, len(allTexts)):
        x = np.size(wordCountMatrix, -1)
        columnVec = np.zeros(x)
        #need preprocessing here!
        for word in preprocessedTexts[textInd]:
            if word in wordArray:
                columnVec[wordArray.index(word)] += 1
            else:
                wordArray.append(word)
                idfValues.append(np.log(len(allTexts)/numOfFilesWithWord(word, preprocessedTexts)))
                columnVec = np.append(columnVec, [1], axis=0)
        columnVec /= textSizes[textInd]
        columnVec *= idfValues
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
            sentence = sentencesInText[sentenceInd]
            words = sentence.split(" ")
            for word in words:
                if word in wordArray:
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
    return(sentenceWeightMatrix, allSentences)
    # print(allSentences)
    print(sentenceWeightMatrix)


def summarise(allTexts, summaryLength):
    countedWords = countWords(textTuple)
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
            elif (lenOfBestSentence + len(summary[x].split(" ")) <= summaryLength) and len(allTexts[x]) != 0:
                summary[x] = summary[x] + bestSentence
            elif (lenOfBestSentence + len(summary[x].split(" ")) > summaryLength) or len(allTexts[x])==0:
                lengthCheckList[x] = True
        countedWords = countWords(allTexts)
        listOfWords = countedWords[0]
        wordCountMatr = countedWords[1]
        docSizes = countedWords[2]
        sentenceWeightsAndSentences = calcSentenceWeights(textTuple, listOfWords, wordCountMatr, docSizes)
        sentenceWeightMatrix = sentenceWeightsAndSentences[0]
        sentences = sentenceWeightsAndSentences[1]
    for summaryText in summary:
        summaryFile.write(summaryText + "\n ---------------------------------------- \n")

summarise(textTuple, 150)
