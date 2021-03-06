import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.corpus import PlaintextCorpusReader
from pattern.en import number
import re

'''
gets the user input lower cases it and tokenizes it
'''
DEBUG = True
FROM_ = 0
TO_ = 0
COPIES_ = 1
isSinglePageRange = False
def preProcessText(sentence):
    keywords = word_tokenize(sentence.lower())
    wordlists = readCorpora()
    #print ("file Ids = ")
    #print wordlists.fileids()
    
    #rewriting the command so that if user  has shortforms or any spelling mistake
    copy_words = wordlists.words("copy_words")
    from_words = wordlists.words("from_words")
    to_words   = wordlists.words("to_words")
    page_words   = wordlists.words("page_words")

    for index, key in enumerate(keywords):
        if(key in copy_words):
            keywords[index] = "copies"

        if(key in from_words):
            keywords[index] = "from"
        if(key in to_words):
            keywords[index] = "to"
        if(key in page_words):
            keywords[index] = "page"
    sentence = " ".join(keywords)
    if(DEBUG):
        print 
    # Produce: "Hello-world"
    
    sentence = re.sub(r'a c\w+'," 1 copies",sentence)
    sentence = re.sub(r'[\W]'," ",sentence)
    sentence = re.sub(r'pages',"page",sentence)
    global isSinglePageRange
    isSinglePageRange = checkIfSinglePageRange(sentence)
    if(isSinglePageRange):
        m = re.findall(r'(?:\S+\s)?\S*page\S*(?:\s\S+)?',(sentence))
        try:
            if m:
                foundPage = m[0];
                if(DEBUG):
                    print "found Page = ";
                    print  foundPage
        except:
            pass
        foundcopies = ""
        m  = re.search(r'(?:\S+\s)?\S*copies\S*(?:\s\S+)?',sentence)
        if m:
            foundcopies = m.group(0)
            if(DEBUG):
                print "found copies " + foundcopies
         
        sentence = foundPage + " " + foundcopies
        if(DEBUG):
            print "sentence = " +  sentence
        tokens = word_tokenize(sentence.lower())
        return tokens
    else:
        #checking if user has given range.example : 3-4 5-7 etc.
        sentence = re.sub(r'\-'," to ",(sentence))
        #removing all special characters from the sentence
        sentence = re.sub(r'a c\w+'," 1 copies",sentence)
        sentence = re.sub(r'[\W]'," ",sentence)
        sentence = re.sub(r'pages',"page",sentence)
   
        if(DEBUG):
            print sentence
        #if the user has given page 4 to page 5 removing it inorder to process the range
        m = re.findall(r'page\S*(?:\s\S+)?',(sentence))
        try:
            if m:
                foundFromPage,foundToPage = m[0],m[1];
                if(DEBUG):
                    print "foundFrom Page = ";
                    print  foundFromPage
                    print "foundToPage = ";
                    print  foundToPage
                foundFromPage = re.sub(r'page','',foundFromPage)
                foundToPage = re.sub(r'page','',foundToPage)
                foundFromPage = re.sub('\W+','',foundFromPage)
                foundToPage = re.sub('\W+','',foundToPage)
        
                if(DEBUG):
                    print "foundFrom Page = ";
                    print  foundFromPage
                    print "foundToPage = ";
                    print  foundToPage
                sentence = re.sub(r'page\S*(?:\s\S+)?',foundFromPage,sentence,count=1,flags=0)
                sentence = re.sub(r'page\S*(?:\s\S+)?',foundToPage,sentence,count=1,flags=0)
                if(DEBUG):
                    print "sentence" + sentence
        except:
            pass 
        m = re.search(r'(?:\S+\s)?\S*to\S*(?:\s\S+)?',sentence)
        found = ""
        if m:
            found = m.group(0)
            if(DEBUG):
                print "found " +  found
        foundcopies = ""
        m  = re.search(r'(?:\S+\s)?\S*copies\S*(?:\s\S+)?',sentence)
        if m:
            foundcopies = m.group(0)
            if(DEBUG):
                print "found copies " + foundcopies
         
        sentence = found + " " + foundcopies
        if(DEBUG):
            print "sentence = " +  sentence
        tokens = word_tokenize(sentence.lower())
        return tokens

def checkIfSinglePageRange(sentence):
    #checking if user has given range.example : 3-4 5-7 etc.
        #removing all special characters from the sentence
        if "page" in sentence and ("to" not in sentence or "from" not in sentence):
            return True
        else:
            return False


'''
reads all our corpus and returns the wordlist
'''
def readCorpora():
    #corpus_root = 'printhen/corpora/corpora'
    corpus_root = 'corpora/corpora'
    wordlists = PlaintextCorpusReader(corpus_root, '.*')
    return wordlists


'''
parses our value based on grammer
'''
def parseValues(keywords,grammar,pagefalse):
    #stop words are words like is, was , from ,to etc.
    stop = set(stopwords.words('english'))
    #adding print to the stop words.
    stop.add("print")
    stop.remove("to")
    if(isSinglePageRange==False):
        stop.add("page")
    #removing stop words
    pure_tokens = [i for i in keywords if i not in stop]
    #parts of speech tagging
    keywords_after_tagging = nltk.pos_tag(pure_tokens)
    if(DEBUG):
        print keywords_after_tagging
    cp = nltk.RegexpParser(grammar)
    #chunking based on grammer
    result = cp.parse(keywords_after_tagging)
    return result

def extract_information(sentence):
    fromToSet = False
    from_ = 0
    to = 0
    copies = 1
    keywords = preProcessText(sentence)
    for index,k in enumerate(keywords):
        'Checking if the number given is ordinal viz. 3rd 5th etc.'
        keywords[index] = re.sub(r'nd$|th$|rd$|st$',"",(k))
    

    if(DEBUG):
        print ("Keywords = ")
        print keywords
    if not keywords:
        from_ = -1
        to = -1
        copies = 1
        d = {}
        d['from'] = str(from_)
        d['to'] = str(to)
        d['copies'] = str(copies)
        return d
    result = parseValues(keywords,'''
            NP: {<NN.>}
            CP: {<CD>}
            TO: {<TO>}
            VP: {<VB.> | <NN>}
            ''',True)
    if(DEBUG):
        print((result))
    #result.draw()
    for index,res in enumerate(result.subtrees()):
        
        if(isSinglePageRange):
            if(res.label() == "CP"):
                if(DEBUG):
                    print "PAGE CP"
                    print fromToSet
                    if(fromToSet == False):
                        if("page" in result[index-2].leaves()[0][0]):
                            for leaf in res.leaves():
                                from_ = number(leaf[0])
                                to = number(leaf[0])
                            fromToSet = True
                        elif("page" in result[index].leaves()[0][0]):
                            for leaf in res.leaves():
                                from_ = number(leaf[0])
                                to = number(leaf[0])
                            fromToSet = True
                        else:
                            pass
        else:
            if res.label() == "TO":
                if(DEBUG):
                    print "TO" 
                    print result[index-2].leaves()
                for leaf in result[index-2]:
                    from_ = number(leaf[0])
                    if(DEBUG):
                        print from_
                if(DEBUG):
                    try:
                        print result[index].leaves()
                    except:
                        print "I didnt quite understand what you said can you rephrase your sentence?"
                        from_ = -1
                        to = -1
                        copies = 1
                        d = {}
                        d['from'] = str(from_)
                        d['to'] = str(to)
                        d['copies'] = str(copies)
                        return d
                for leaf in result[index]:
                    to = number(leaf[0])
                    if(DEBUG):
                        print to
                if(DEBUG):
                    print "TO"
        if res.label() == "NP":
            if(DEBUG):
                print "COPIES"
            try: 
                if(DEBUG):
                    try:
                        print result[index-2].leaves()
                    except:
                        print "I didnt quite understand what you said can you rephrase your sentence?"
                        from_ = -1
                        to = -1
                        copies = 1
                        d = {}
                        d['from'] = str(from_)
                        d['to'] = str(to)
                        d['copies'] = str(copies)
                        return d
                for leaf in result[index-2]:
                    if(to!=number(leaf[0])):
                        if(leaf[1]=="CD"):
                            copies = number(leaf[0])
                            if(DEBUG):
                                print "if copies"
                                print copies
                    else:
                        for leaf in result[index]:
                            if(leaf[1]=="CD"):
                                copies = number(leaf[0])
                                if(DEBUG):
                                    print "else copies"
                                    print copies
            except:
                    try:
                        for leaf in result[index]:
                            if(leaf[1]=="CD"):
                                copies =  number(leaf[0])
                                if(DEBUG):
                                    print "except copies"
                                    print copies
                    except:
                        copies = to
                        if(DEBUG):
                            print "TO = COPIES"
    
    if(from_ == 0 or to == 0):
        print "\n"
        print "\n"
        print "\n"
        print "it seems like you want to print " + str(copies)+" copies of the whole document"
        from_=-1
        to=-1
    print "\n"
    print "\n"
    print "\n"
    print "it seems like you want to print " + str(copies) +" copies of the document " + "from pages " + str(from_) + " to " + str(to)
    print "\n"
    print "Have I guessed correctly :)?"
    d = {}
    d['from'] = str(from_)
    d['to'] = str(to)
    d['copies'] = str(copies)
    return d

def getFrom():
    return FROM_

def getTo():
    return TO_

def getCopies():
    return COPIES_

if __name__ == "__main__":
    sentence = raw_input("Enter your Command")
    extract_information(sentence)
