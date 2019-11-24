#python=3.6
# -*- coding: utf-8 -*-
"""
Synopsis: 

Created: Sun Nov 24 15:34:46 2019

Sources:

Author:   John Telfeyan
          john <dot> telfeyan <at> gmail <dot> com

Distribution: MIT Opens Source Copyright; Full permisions here:
    https://gist.github.com/john-telfeyan/2565b2904355410c1e75f27524aeea5f#file-license-md
         
"""


import nltk


def pos_sentence_filter( sentence, pos = ['NN', 'NS'], download_nltk_resources=False):
    ''' Given a sentence and part-of-speach codes, return only words matching that pos
    
        Args:
            sentence (string) : one string
            pos (list or string) : part of speach to filter in
            download_nltk_resources (bool) : set to true to auto-download 
                required models
            
        Returns: 
            filterd list of words
            
        Requires:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
        
        POS Lables:
            CC coordinating conjunction
            CD cardinal digit
            DT determiner
            EX existential there (like: "there is" ... think of it like "there exists")
            FW foreign word
            IN preposition/subordinating conjunction
            JJ adjective 'big'
            JJR adjective, comparative 'bigger'
            JJS adjective, superlative 'biggest'
            LS list marker 1)
            MD modal could, will
            NN noun, singular 'desk'
            NNS noun plural 'desks'
            NNP proper noun, singular 'Harrison'
            NNPS proper noun, plural 'Americans'
            PDT predeterminer 'all the kids'
            POS possessive ending parent's
            PRP personal pronoun I, he, she
            PRP$ possessive pronoun my, his, hers
            RB adverb very, silently,
            RBR adverb, comparative better
            RBS adverb, superlative best
            RP particle give up
            TO to go 'to' the store.
            UH interjection errrrrrrrm
            VB verb, base form take
            VBD verb, past tense took
            VBG verb, gerund/present participle taking
            VBN verb, past participle taken
            VBP verb, sing. present, non-3d take
            VBZ verb, 3rd person sing. present takes
            WDT wh-determiner which
            WP wh-pronoun who, what
            WP$ possessive wh-pronoun whose
            WRB wh-abverb where, when
    '''
    try:
        tokens   = nltk.word_tokenize(sentence)
        tags     = nltk.pos_tag(tokens)
    except LookupError:
        if download_nltk_resources:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
        else:
            raise LookupError 
        
    filtered = [word for word, word_pos in tags if word_pos in pos]
    return filtered


if __name__=="__main__":
    
    
    doc = """I absolutly hate drinking sparkingly water.  When Douglas built 
    his house it started a town. When the grocery store is out of coffee it is 
    imparative to speak with the manager. When walking upon the trail Pete realized
    his shoelace was untied.
    """
    
    # Test part of speach filter
    sentences = nltk.tokenize.sent_tokenize(doc)
    for sentence in sentences:
        nouns = pos_sentence_filter(sentence)
        print (nouns)