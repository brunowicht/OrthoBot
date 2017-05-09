# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 15:33:15 2017

@author: bruno
"""

import time
import requests
from bs4 import BeautifulSoup

letters = ['a', 'c', 'p', 'e', 'l', 'o', 'n', 't', 'r', 'i', 'f', 'g',
           'j', 'u', "'", 's', 'b', 'd', 'v', '-', 'm', 'z', 'è', 'é', 'q', 'â',
           'y', 'x', 'h', 'k', 'î', 'ê', 'û', 'ç', 'ë', 'ï', 'ô', 'ö', 'à', 'w',
           'ü', 'ñ', 'ù', 'ã', '.']

baseurl='http://wikipast.epfl.ch/wikipast/'
user = 'Orthobot'
passw = 'orthobot2017'
summary='Wikipastbot update'

# Login request
payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
r1=requests.post(baseurl + 'api.php', data=payload)

#login confirm
login_token=r1.json()['query']['tokens']['logintoken']
payload={'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
r2=requests.post(baseurl + 'api.php', data=payload, cookies=r1.cookies)

#get edit token2
params3='?format=json&action=query&meta=tokens&continue='
r3=requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
edit_token=r3.json()['query']['tokens']['csrftoken']

edit_cookie=r2.cookies.copy()
edit_cookie.update(r3.cookies)



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

def read_corrections():
    file = open('corrections.txt', 'r', encoding='utf8')
    cor = {}
    w = file.readline()
    while w:
        word = w.split(':')
        cor[word[0]] = word[1].split(',')
        w = file.readline()
    file.close()
    return cor

words = read_french_words()
corrections = read_corrections()


def write_corrections(t):
    file = open('corrections.txt', 'a', encoding='utf8')
    file.write(t)
    file.close()
    
    
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


def remove_colored(text):
    #color removing
    text = text.replace('<span style="color:red">', '<')
    text = text.replace('<span style="color:green">', '<')
    text = text.replace('</span>', '>')
    #no wiki removing (code)
    text = text.replace('<nowiki>', '<')
    text = text.replace('/nowiki>', '>')
    #table removing (a lot of names in there)
    text = text.replace('{|', '<')
    text = text.replace('|}', '>')
    return text
            

def keep_only_letters(text):
    """return the same text removing all character which is not a letter or a space."""
    t = ''
    for c in text:
        if c == '’':
            c = "'"
        if c.lower() in letters or c == ' ':
            t += c.lower()
        else:
            t += ' '
    return t+' '

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
    text_words = eliminate_tirait_apostrophe(text_to_words(keep_only_letters(remove_bracketed(remove_balised(remove_colored(text)), hypermots))))
    false_words = list()
    for w in text_words:
        if not word_correct(w):
            false_words.append(w)
    return false_words

def correction_proposition(word):
    """propose a correction for a erroneous word"""
    if word_correct(word):
        return [word]
    cor = list()
    
    ## 1 letter wrong
    for i in range(len(word)):
        for l in letters:
            cword = ''
            cword += word[:i]
            cword += l
            if i < len(word)-1:
                cword += word[i+1:]
            if word_correct(cword):
                cor.append(cword)
    
    
    ## 1 letter missing            
    for i in range(len(word)+1):
        for l in letters:
            cword = ''
            cword += word[:i]
            cword += l
            if i < len(word):
                cword += word[i:]
            if word_correct(cword):
                cor.append(cword)
                
                
    for i in range(len(word)):
        cword = ''
        cword += word[:i]
        if i < len(word)-1:
            cword += word[i+1:]
        if word_correct(cword):
            cor.append(cword)
    


        
    ##special patterns
    for i in range(len(word)):
        if word[i] == 'f':
            cword = ''
            cword += word[:i]
            cword += 'ph'
            if i < len(word)-1:
                cword += word[i+1:]
            if word_correct(cword):
                cor.append(cword)
        
    
    
    
    ## to make each correction unique
    return list(set(cor))

def corrections_for_words(word):
    unique_w = list(set(word))
    for w in unique_w:
        if not w in corrections:
            corrections[w] = correction_proposition(w)
            c = w
            c += ':'
            c += ','.join(corrections[w])
            c += '\n'
            write_corrections(c)
                


def print_correct_proposition_text(text):
    wrong = text_wrong_words(text, False)
    corrections_for_words(wrong)
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
    text = text+' '
    wrong = list(set(text_wrong_words(text, False)))
    corrections_for_words(wrong)
    for w in wrong:
        i = text.find(w)
        l = len(w)
        while i in range(0, len(text)):
            if i > 0 and not text[i-1].isalpha() and not text[i+l].isalpha():
                text = text[:i]+ '<span style="color:red">' +text[i:i + l] + '</span> (correction(s): <span style="color:green">' +', '.join(corrections[w])+'</span>)'+ text[i + l:]
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
           
def edit_page(page, text):
    payload = {'action':'edit','assert':'user','format':'json','utf8':'','text': text,'summary':summary,'title':page,'token':edit_token}     
    requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
    


def main():
    t = time.time()
    pages = getPageList()
    for p in pages:
        if not (p.find('Fichier') == 0 or p in ['Monsieur Y', 'Madame X', 'Biographies']):
            print(p)
            corrected = correct_in_text(get_text(p))
            #edit_page(p, corrected)
    print(time.time() - t)

main()
#Questions à poser:
    #Que faire des hypermots?
    #Comment proposer une correction à l'utilisateur? écrire le mot en rouge 
    #et mettre ses corrections dans la discussion
    #doit on "infecter" le site?
    #<span style="color:red">texte rouge</span> donne "texte rouge" en rouge dans la sytaxe wiki
    #password orthobot: orthobot2017