# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:33:15 2017

@author: bruno
"""

import time
import requests
from bs4 import BeautifulSoup

def read_french_words():
    """read the dictionary txt file and store all the french words in a list"""
    file = open('french_words.txt','r', encoding='utf8')
    
    words = list()
    w = file.readline()
    while w:
        words.append(w[:-1])
        w = file.readline()
        
    file.close()   
    return words

words = read_french_words()
letters = ['a', 'c', 'p', 'e', 'l', 'o', 'n', 't', 'r', 'i', 'f', 'g',
           'j', 'u', "'", 's', 'b', 'd', 'v', '-', 'm', 'z', 'è', 'é', 'q', 'â',
           'y', 'x', 'h', 'k', 'î', 'ê', 'û', 'ç', 'ë', 'ï', 'ô', 'ö', 'à', 'w',
           'ü', 'ñ', 'ù', 'ã', '.']

baseurl='http://wikipast.epfl.ch/wikipast/'


def word_correct(w):
    """Returns True if word w is correct i.e. if it is in the dictionary"""
    w = w.lower()
    return w in words or w == ''

def remove_bracketed(text, keep_hypermot = False):
    """remove all the hypermots and links between brackets"""
    t = ''
    bracket = 0
    for c in text:
        if c == '[':
            bracket += 1
        if c == ']' and bracket > 0:
            bracket -= 1
        elif bracket == 0:
            t += c
        elif bracket == 2 and keep_hypermot:
            t += c
    return t

def remove_balised(text):
    """remove all the balises"""
    t = ''
    b = 0
    for c in text:
        if c == '<':
            b += 1
        if c == '>' and b > 0:
            b -= 1
        elif b == 0:
            t += c
    return t
            

def keep_only_letters(text):
    """return the same text removing all character which is not a letter or a space."""
    t = ''
    for c in text:
        if c == '’':
            c = "'"
        if c.lower() in letters or c == ' ':
            t += c.lower()
    return t

def text_to_words(text):
    """transforms a text into a list of words"""
    word = text.split(' ')
    ws = list()
    for w in word:
        if contains_letter(w):
            ws.append(w)
    return ws

def contains_letter(word):
    for c in word:
        if c.isalpha():
            return True
    return False
            

def eliminate_tirait_apostrophe(word_list):
    word = list()
    for w in word_list:
        if "'" in w:
            if word_correct(w):
                word.append(w)
            else:
                w1 = w.split("'")
                for w2 in w1:
                    if not w2 == '':
                        word.append(w2)
        else:
            word.append(w)
    word2 = list()
    for w in word:
        if '.' in w:
            if word_correct(w):
                word2.append(w)
            else:
                w1 = w.split('.')
                for w2 in w1:
                    if not w2 == '':
                        word2.append(w2)
        else:
            word2.append(w)
            
    final_word = list()
    for w in word2:
        if "-" in w:
            if word_correct(w):
                word.append(w)
            else:
                w1 = w.split("-")
                for w2 in w1:
                    if not w2 == '':
                        final_word.append(w2)
        else:
            final_word.append(w)
    return final_word
                

def text_wrong_words(text, hypermots=False):
    text_words = eliminate_tirait_apostrophe(text_to_words(keep_only_letters(remove_bracketed(remove_balised(text), hypermots))))
    false_words = list()
    for w in text_words:
        if not word_correct(w):
            false_words.append(w)
    return false_words

def correction_proposition(word):
    """propose a correction for a erroneous word"""
    if word_correct(word):
        return [word]
    corrections = list()
    
    ## 1 letter wrong
    for i in range(len(word)):
        for l in letters:
            cword = ''
            cword += word[:i]
            cword += l
            if i < len(word)-1:
                cword += word[i+1:]
            if word_correct(cword):
                corrections.append(cword)
    
    
    ## 1 letter missing            
    for i in range(len(word)):
        for l in letters:
            cword = ''
            cword += word[:i]
            cword += l
            if i < len(word)-1:
                cword += word[i:]
            if word_correct(cword):
                corrections.append(cword)
                
                
    for i in range(len(word)):
        cword = ''
        cword += word[:i]
        if i < len(word)-1:
            cword += word[i+1:]
        if word_correct(cword):
            corrections.append(cword)
    


        
    ##special patterns
    for i in range(len(word)):
        if word[i] == 'f':
            cword = ''
            cword += word[:i]
            cword += 'ph'
            if i < len(word)-1:
                cword += word[i+1:]
            if word_correct(cword):
                corrections.append(cword)
        
    
    
    
    ## to make each correction unique
    return list(set(corrections))

def corrections_for_words(word):
    cor = {}
    unique_w = list(set(word))
    for w in unique_w:
        cor[w] = correction_proposition(w)
    return cor

def print_correct_proposition_text(text):
    wrong = text_wrong_words(text, False)
    corrections = corrections_for_words(wrong)
    for w in wrong:
        print(w + '\ncorrection: ' + str(corrections[w]))
        print('')


def get_text(page_name):
    
    
    result=requests.post(baseurl+'api.php?action=query&titles='+page_name+'&export&exportnowrap')
    soup=BeautifulSoup(result.text, "lxml")
    text=''
    for primitive in soup.findAll("text"):
        text+=primitive.string
    return text
    
def correct_in_text(text):
    wrong = list(set(text_wrong_words(text, False)))
    corrections = corrections_for_words(wrong)
    for w in wrong:
        i = text.find(w)
        l = len(w)
        while i in range(0, len(text)):
            if i > 0 and not text[i-1].isalpha() and not text[i+l].isalpha():
                text = text[:i]+ '<span style="color:red">' +text[i:i + l] + '</span> {corrections: <span style="color:green">' +str(corrections[w])+'</span>}'+ text[i + l:]
            i = text.find(w, i+25)
            
    return text
                
def getPageList():
    protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","IB","SourceBot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
    pages=[]
    for user in protected_logins:
        result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend=2017-02-02T16:00:00Z')
        soup=BeautifulSoup(result.content,'lxml')
        for primitive in soup.usercontribs.findAll('item'):
            pages.append(primitive['title'])
    return list(set(pages))
           
        

def main():
    t = time.time()
    corrected = correct_in_text(get_text('TestOrthobot'))
    print(corrected)
    print(time.time()-t)

#Questions à poser:
    #Que faire des hypermots?
    #Comment proposer une correction à l'utilisateur? écrire le mot en rouge 
    #et mettre ses corrections dans la discussion
    #doit on "infecter" le site?
    #<span style="color:red">texte rouge</span> donne "texte rouge" en rouge dans la sytaxe wiki
    #password orthobot: orthobot2017