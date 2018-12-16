import json
import nltk
import tqdm

from FreelingDictionary import FreelingDictionary

from nltk import (
    ngrams,
    wordpunct_tokenize as tokenizer
)

from tqdm import tqdm


#   Source: https://www.englishpage.com/verbpage/verbtenseintro.html




class Perfectivity:
    def __init__(self):
        return

    def __call__(self, dictionary, gram):
        # contiguous or nearly-contiguous
        # form of 'to have' and past participle:
        for i in range(len(gram) - 1):
            curr = gram[i]
            next = gram[i + 1]
            if dictionary.to_have(curr) \
            and dictionary.is_participle(next):
                return True
        return False


class Continuity:
    def __init__(self):
        return

    def __call__(self, dictionary, gram):
        for i in range(len(gram) - 1):
            curr = gram[i]
            next = gram[i + 1]
            if dictionary.is_gerund(next) \
            and not dictionary.to_go(next) \
            and dictionary.to_be(curr):
                return True
        return False


class Arrow:
    def __init__(self):
        return
    
    def __call__(self, dictionary, gram):
        
        #   test for future ('will' + VB)
        if len(gram) > 1 and gram[0] == 'will':
            for next in gram[1:]:
                if dictionary.is_base_form(next) \
                and dictionary.is_lexically_consistent(gram[:gram.index(next)]):
                    return 'future'
        
        #   test for future ('going to' + VB)
        elif len(gram) > 3 and dictionary.to_be(gram[0]):
            for i in range(1, len(gram) - 2):
                go = gram[i]
                for j in range(i + 1, len(gram) - 1):
                    to = gram[j]
                    if to == 'to' \
                    and dictionary.is_gerund(go) \
                    and dictionary.to_go(go) \
                    and dictionary.is_lexically_consistent(gram[1:j]):
                        return 'future'

        #   test for past (VBD)
        elif dictionary.is_past(gram[0]):
            return 'past'

        #   test for present (VBP, VBZ)
        elif dictionary.is_present(gram[0]):
            return 'present'
        
        else:
            return 'unknown'



class VerbTense:
    def __init__(self):
        self.arrow = Arrow()
        self.continuity = Continuity()
        self.perfectivity = Perfectivity()
        


#   Presents
class SimplePresent(VerbTense):
    def __call__(self, dictionary, gram):
        if len(gram) == 1 \
        and self.arrow(dictionary, gram) == 'present' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram):
            return True
        return False
    
    def name(self):
        return 'SimplePresent'

class PresentPerfect(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'present' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PresentPerfect'

class PresentContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'present' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PresentContinuous'

class PresentPerfectContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'present' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PresentPerfectContinuous'


#   Pasts
class SimplePast(VerbTense):
    def __call__(self, dictionary, gram):
        if len(gram) == 1 \
        and self.arrow(dictionary, gram) == 'past' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram):
            return True
        return False
    
    def name(self):
        return 'SimplePast'

class PastContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'past' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PastContinuous'

class PastPerfect(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'past' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PastPerfect'

class PastPerfectContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'past' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'PastPerfectContinuous'


# Futures
class SimpleFuture(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'future' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_base_form(gram[-1]) \
        and not [w for w in gram[:-1] if dictionary.is_base_form(w)]:
            return True
        return False
    
    def name(self):
        return 'SimpleFuture'

class FutureContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'future' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'FutureContinuous'

class FuturePerfect(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'future' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'FuturePerfect'

class FuturePerfectContinuous(VerbTense):
    def __call__(self, dictionary, gram):
        if self.arrow(dictionary, gram) == 'future' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            return True
        return False
    
    def name(self):
        return 'FuturePerfectContinuous'



class VerbTenseRecognizer:

    def __init__(self, min_gram=1, max_gram=6):
        self.dictionary = FreelingDictionary()
        self.min_gram = min_gram
        self.max_gram = max_gram
        self.tenses = [

            PresentPerfectContinuous(),
            PastPerfectContinuous(),
            FuturePerfectContinuous(),
    
            PresentPerfect(),
            PresentContinuous(),
            PastPerfect(),
            PastContinuous(),
            FuturePerfect(),
            FutureContinuous(),
            
            SimplePresent(),
            SimplePast(),
            SimpleFuture()

        ]
    
    def __call__(self, tokens):
        matches = []
        covered = set([])
        for n in range(self.max_gram, self.min_gram - 1, -1):
            for i, gram in enumerate(ngrams(tokens, n)):
                start = i
                end = i + n
                area = set(range(start, end))
                if area.intersection(covered):
                    continue
                for tense in self.tenses:
                    match = tense(self.dictionary, gram)
                    if match:
                        covered.update(area)
                        o = {
                            'start': start,
                            'end': end,
                            'text': ' '.join(tokens[start:end]),
                            'tense': tense.name()
                        }
                        print gram, '\t', tense.name(), '\t', match
                        print json.dumps(o, indent=4)
                        break


# Training a model using NLTK for recognising tenses

#   for negatives verbs:
#       1. expand negative contractions
#       2. if negative, generate positive
#       3. check tense normally



if __name__ == '__main__':

    vtr = VerbTenseRecognizer()
    
    tests = [
        'I study English every day.',
        'I am studying English now.',
        'I have studied English in several different countries.',
        'I have been studying English for five years.',
        'Two years ago, I studied English in England.',
        'I was studying English when you called yesterday.',
        'I had studied a little English before I moved to the U.S.',
        'I had been studying English for five years before I moved to the U.S.',
        'If you are having problems, I will help you study English.',
        'I will be studying English when you arrive tonight.',
        'I will have studied every tense by the time I finish this course.',
        'I will have been studying English for over two hours by the time you arrive.',
        
        'I am going to study English next year.',    # exception!
        'I am going to be studying English when you arrive tonight.',
        'I am going to have studied every tense by the time I finish this course.',
        'I am going to have been studying English for over two hours by the time you arrive.'
    ]
    for test in tests:
        tokens = tokenizer(test)
        print
        print tokens
        vtr(tokens)
