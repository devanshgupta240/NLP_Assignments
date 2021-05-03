# -*- coding: utf-8 -*-
"""LinearInterpolation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14FXlU3ZEuNgWwSkSgdRkByUplxVjWdiI
"""

!pip install nltk

import nltk
nltk.download('popular')

from nltk.tokenize import sent_tokenize, word_tokenize

with open('/content/drive/My Drive/shortCorpus.txt') as f:
  text = f.read()

sentenceTokens = sent_tokenize(text)

import random

random.shuffle(sentenceTokens)

noOfSen = len(sentenceTokens)
partIndex = int((noOfSen*9)/10)

trainAndDev = sentenceTokens[:partIndex]
test = sentenceTokens[partIndex:]

noOfSenTandD = len(trainAndDev)
partITandD = int((noOfSenTandD*9)/10)

import itertools
import operator
import collections
from collections import Counter
import matplotlib.pyplot as plt
from nltk.util import ngrams
from scipy.stats import binom 
import math
from decimal import *

"""Function For Padding Start and End"""

start = "S123T S123T "
end = " E321D"

def padStartandEnd(listOfSen):
  noOfSen = len(listOfSen)
  for i in range(noOfSen):
    listOfSen[i] = start + listOfSen[i] + end
  return listOfSen

"""Function For Removing Unwanted Tokens"""

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

"""Function For Tokenizing All Sentences"""

def tokenizeAllSentences(listOfSen):
  allWordTokens = []
  for sen in listOfSen:
    allWordTokens.extend(word_tokenize(sen))
  return allWordTokens

"""Function For Replacing tokens in sentence which are not present in Vocab or have Less Frequency"""

def replacelessfreq(listOfTokensinSen,freqWordsTraining):
  for i in range(len(listOfTokensinSen)):
    if (listOfTokensinSen[i] in freqWordsTraining):
        if (freqWordsTraining[listOfTokensinSen[i]]<10):
            #print(listOfTokensinSen[i]," ",freqWordsTraining[listOfTokensinSen[i]])
            listOfTokensinSen[i] = 'U345K'
    else:
      #print(listOfTokensinSen[i])
      if (listOfTokensinSen[i]!='S123T' and listOfTokensinSen[i]!='E321D'):
          listOfTokensinSen[i] = 'U345K'
  return listOfTokensinSen

"""Function For Replacing tokens in all sentence and return list of tokens for all sentences"""

def replaceAndReturnTokenlist(listOfSen,freqWordsTraining):
  replacedTokensListofAllSen = []
  for sen in listOfSen:
    #temp = remove_values_from_list(word_tokenize(sen), '.')
    listOfTokensinSen = word_tokenize(sen)
    listOfTokensinSen = replacelessfreq(listOfTokensinSen,freqWordsTraining)
    replacedTokensListofAllSen.append(listOfTokensinSen)
  return replacedTokensListofAllSen

"""Total no. of words (they may be same)"""

def totalWords(freqDict):
  totalfreq = 0;
  for val in freqDict:
    totalfreq += freqDict[val]
  return totalfreq

"""Interpolation Function"""

def probabOfSentenceLI(trigramsListSen,totalFreqUnigram,freqUnigram,freqBigram,freqTrigram,coff1,coff2,coff3):
  probabSen =0
  for elm in trigramsListSen:
    temp =0;
    u = elm[0]
    v = elm[1]
    w = elm[2]
    #print(u," ",v," ",w)
    if (u,v,w) in freqTrigram:
      #print("Trigram Freq ",freqTrigram[(u,v,w)]," ",freqBigram[(u,v)])
      temp += coff1*(freqTrigram[(u,v,w)]/freqBigram[(u,v)])

    if (v,w) in freqBigram:
      #print("Bigram Freq ",freqBigram[(v,w)]," ",freqUnigram[v])
      temp += coff2*(freqBigram[(v,w)]/freqUnigram[v])

    if w in freqUnigram:
      #print("Unigram Freq ",freqUnigram[w]," ", totalFreqUnigram)
      temp += coff3*(freqUnigram[w]/totalFreqUnigram)

    probabSen += math.log(temp,2)
  return probabSen

"""Laplace Probability of Sentence"""

def probabOfSentenceLaplace(trigramsListSen,freqBigram,freqTrigram,sizeOfVocabulary):
  probabSen =0
  for elm in trigramsListSen:
    temp =0;
    u = elm[0]
    v = elm[1]
    w = elm[2]
    #print(u," ",v," ",w)
    if (u,v,w) in freqTrigram:
      temp = (freqTrigram[(u,v,w)]+1)/(freqBigram[(u,v)]+sizeOfVocabulary)
    else:
      if (u,v) in freqBigram:
        temp = 1/(freqBigram[(u,v)]+sizeOfVocabulary)
      else:
        temp = 1/(sizeOfVocabulary)
    probabSen += math.log(temp,2)
  return probabSen

"""Perplexity Function"""

def calculatePerplexity(M,totalLogProbAllSen):
  l = (totalLogProbAllSen/M)
  return pow(2,-1*l)

"""Function For randomly choosing train and dev set and analysing"""

def createTrainingAndDevAndTestforAllLambda():
  random.shuffle(trainAndDev)

  train = trainAndDev[:partITandD]
  dev = trainAndDev[partITandD:]

  print("length of train: ",len(train))
  print("length of dev: ",len(dev))

  train = padStartandEnd(train)
  print("")
  print("padding done in training")
  #train[:10]

  wordTokensTrain = tokenizeAllSentences(train)
  freqWords = dict(Counter(wordTokensTrain))

  replacedTokenListAllSenTrain = replaceAndReturnTokenlist(train,freqWords)
  print("")
  print("lower frequency words replaced in train")
  #replacedTokenListAllSenTrain[:2]

  unigrams = []
  for sen in replacedTokenListAllSenTrain:
    unigrams.extend(sen)
  print("")
  print("unigrams extracted")
  #unigrams[:10]

  freqUnigram = dict(Counter(unigrams))

  freqList = list(freqUnigram.values())
  bins = [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,50]
  print("")
  print("Verifying Lower frequency words Removed in train")
  #plt.hist(freqList,bins=bins,edgecolor='black')

  bigrams = []
  for sen in replacedTokenListAllSenTrain:
    bigrams.extend(list(ngrams(sen,2)))
  print("")
  print("bigrams extracted")
  #bigrams[:10]

  freqBigram = dict(Counter(bigrams))

  trigrams = []
  for sen in replacedTokenListAllSenTrain:
    trigrams.extend(list(ngrams(sen,3)))
  print("")
  print("trigrams extracted")
  #trigrams[:10]

  freqTrigram = dict(Counter(trigrams))
  print("")
  print("Number of distinct words remain: ",len(freqUnigram))
  totalFreqUnigram = totalWords(freqUnigram) - freqUnigram['S123T']
  print("Total number of words: ",totalFreqUnigram)

  dev = padStartandEnd(dev)
  print("")
  print("padding done in dev")
  #dev[:10]

  replacedTokenListAllSenDev = replaceAndReturnTokenlist(dev,freqWords)
  print("")
  print("lower frequency and out of vocab words replaced in dev")
  #replacedTokenListAllSenTrain[:2]

  lambda1s  = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]
  lambda2s  = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]
  for lambda1 in lambda1s:
    for lambda2 in lambda2s:
      if ((lambda2 + lambda1)<1):

        lambda3 = 1 - (lambda2 + lambda1)
        M = 0
        totalLogProbAllSen =0
        for sen in replacedTokenListAllSenDev:
          trigramsListSen = list(ngrams(sen,3))
          M += len(trigramsListSen)
          pOfSen = probabOfSentenceLI(trigramsListSen,totalFreqUnigram,freqUnigram,freqBigram,freqTrigram,lambda1,lambda2,lambda3)
          #print(pOfSen)
          totalLogProbAllSen += pOfSen

        print("")
        print("For lambda1 =",lambda1," lambda2 =",lambda2," lambda3 =",lambda3)

        print("M = ",M)

        lgLikelihood = totalLogProbAllSen
        print("log likelihood = ",lgLikelihood)

        perplexity = calculatePerplexity(M,totalLogProbAllSen)
        print("Perplexity = ",perplexity)

"""1st Set of Train and Dev"""

createTrainingAndDevAndTestforAllLambda()

"""2nd Set of Train and Dev

"""

createTrainingAndDevAndTestforAllLambda()

"""3rd Set of Train and Dev"""

createTrainingAndDevAndTestforAllLambda()

"""4th Set of Train and Dev"""

createTrainingAndDevAndTestforAllLambda()

"""5th Set of Train and Dev"""

createTrainingAndDevAndTestforAllLambda()

"""**Finally Analysing for Test Set**"""

lambda1 = 0.2
lambda2 = 0.5
lambda3 = 0.3

train = trainAndDev[:partITandD]

print(len(train))
print(len(test))

train = padStartandEnd(train)
train[:10]

wordTokensTrain = tokenizeAllSentences(train)
freqWords = dict(Counter(wordTokensTrain))

replacedTokenListAllSenTrain = replaceAndReturnTokenlist(train,freqWords)
replacedTokenListAllSenTrain[:10]

"""N-Grams Frequency Calculation for Training Set"""

unigrams = []
for sen in replacedTokenListAllSenTrain:
  unigrams.extend(sen)

freqUnigram = dict(Counter(unigrams))

unigrams[:20]

"""Verifying No. Unigram have less frequency now"""

freqList = list(freqUnigram.values())
bins = [1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,50]
plt.hist(freqList,bins=bins,edgecolor='black')

bigrams = []
for sen in replacedTokenListAllSenTrain:
  bigrams.extend(list(ngrams(sen,2)))

freqBigram = dict(Counter(bigrams))

bigrams[:20]

trigrams = []
for sen in replacedTokenListAllSenTrain:
  trigrams.extend(list(ngrams(sen,3)))

freqTrigram = dict(Counter(trigrams))

trigrams[:20]

totalFreqUnigram = totalWords(freqUnigram)- freqUnigram['S123T']

print(len(freqUnigram))
print(totalFreqUnigram)

test = padStartandEnd(test)

test[:10]

replacedTokenListAllSenTest = replaceAndReturnTokenlist(test,freqWords)

"""Applying InterPolation"""

M =0
totalLogProbAllSen =0
for sen in replacedTokenListAllSenTest:
  trigramsListSen = list(ngrams(sen,3))
  M += len(trigramsListSen)
  pOfSen = probabOfSentenceLI(trigramsListSen,totalFreqUnigram,freqUnigram,freqBigram,freqTrigram,lambda1,lambda2,lambda3)
  #print(pOfSen)
  totalLogProbAllSen += pOfSen

print(M)

lgLikelihood = totalLogProbAllSen
print(lgLikelihood)

perplexity = calculatePerplexity(M,totalLogProbAllSen)
print(perplexity)

"""Applying Laplace Smoothing on test"""

M =0
totalLogProbAllSen =0
for sen in replacedTokenListAllSenTest:
  trigramsListSen = list(ngrams(sen,3))
  M += len(trigramsListSen)
  pOfSen = probabOfSentenceLaplace(trigramsListSen,freqBigram,freqTrigram,len(freqUnigram))
  #print(pOfSen)
  totalLogProbAllSen += pOfSen

print(M)

lgLikelihood = totalLogProbAllSen
print(lgLikelihood)

perplexity = calculatePerplexity(M,totalLogProbAllSen)
print(perplexity)