# -*- coding: utf-8 -*-
#python=3.6
"""
Synopsis: lightweight and robust password generator

Created: Created on Thu Feb 21 21:41:05 2019

Sources:

Author:   John Telfeyan
          john <dot> telfeyan <at> gmail <dot> com

Distribution: MIT Opens Source Copyright; Full permisions here:
    https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
         
"""

from json import load
from secrets import choice
from random import shuffle
from linecache import getline

def generate_password(length=16,
                      requirements={"mixed_alphabet": 2,
                                    "digits": 2,
                                    "harmless_symbols": 2 }, 
                      source_dict = "password_source_dict.json"
                      ):
    """
    """
    with open(source_dict, 'r') as f:
        source_chars = load(f)
    try:
        src = { k: source_chars[k] for k in list(requirements.keys()) }
    except KeyError as err:
        raise Exception('KeyError: requirments must match a key in source_dict.') from err
        
    password = ""
    for rule in requirements:
        password = password.join(choice(src[rule]) for i in range(int(requirements[rule])))
    allowed_chars = ''.join( str(s) for s in src.values() )

    add_chars = length - len(password)
    password = password + ''.join( choice(allowed_chars) for i in range(add_chars))
    password = list(password)
    shuffle(password)
    return ''.join(password)
    
    

def awesome_animal(animals = "animal_names.txt",
                   adjectives = "awesome_adjectives.json",
                   alliteration = True):
    """ Generate an Adjective Animal Combination
    """
    with open(animals, 'r') as f:
        beasts = f.readlines()
    with open(adjectives, 'r') as f:
        adjs = load(f)
    adj = choice(list(adjs.keys()))
    if alliteration:
        beasts = list(filter(lambda s: s.startswith(adj[0]), beasts))
    beast = choice(beasts)
    return adj.rstrip('\n').title()+" "+beast.rstrip('\n').title()
    
def provocative_predicate (verb_list = "vivid_verbs.txt",
                           direct_objects = "filterd_unix_wordlist.txt"):
    """
    """
    word_pos = choice(range(file_len(direct_objects)))
    dir_obj = getline(direct_objects, word_pos)
    word_pos = choice(range(file_len(verb_list)))
    verb = getline(verb_list, word_pos)
    
    return verb.strip().title() + " " + dir_obj.strip().title()
    
def passphrase(min_length = 24, requirements = {"digits" : 2, 
                                                "harmless_symbols": 2}):
    
    """
    """
    phrase = awesome_animal() + provocative_predicate()
    phrase = phrase.replace(" ", "")
    allowed = "abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM"
    checked = ""
    for c in phrase:
        if c in allowed:
            checked += c
    
    add_chars = min_length - len(phrase)
    requirements["mixed_alphabet"] = 0
    #print(requirements)
    extra_chars = generate_password( length= add_chars, requirements=requirements )
    
    return phrase + extra_chars
    
    
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
    


"""
if __name__=="__main__":
"""
