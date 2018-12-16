import json
import nltk
import os
import tqdm

from FreelingDictionary import FreelingDictionary

from nltk import (
    ngrams,
    wordpunct_tokenize as tokenizer
)

from Tools import (
    from_csv,
    pyclean
)

from tqdm import tqdm

from VerbProbabilities import UMBC



#   Source: https://www.englishpage.com/verbpage/verbtenseintro.html

class Perfectivity:
    def __init__(self):
        self.index = -1

    def __call__(self, dictionary, gram):
        # contiguous or nearly-contiguous
        # form of 'to have' and past participle:
        for i in range(len(gram) - 1):
            curr = gram[i]
            for j in range(i + 1, len(gram)):
                next = gram[j]
                if dictionary.to_have(curr) \
                and dictionary.is_participle(next) \
                and dictionary.is_lexically_consistent(gram[i:j]):
                    self.index = i
                    return True
        return False


class Continuity:
    def __init__(self):
        self.index = -1

    def __call__(self, dictionary, gram):
        for i in range(len(gram) - 1):
            curr = gram[i]
            for j in range(i + 1, len(gram)):
                next = gram[j]
                if dictionary.is_gerund(next) \
                and not dictionary.to_go(next) \
                and dictionary.to_be(curr) \
                and dictionary.is_lexically_consistent(gram[i:j]):
                    self.index = i
                    return True
        return False


class Arrow:
    def __init__(self):
        self.index = -1
    
    def __call__(self, dictionary, gram):
        
        #   test for future ('will' + VB)
        if len(gram) > 1 and gram[0] == 'will':
            for next in gram[1:]:
                if dictionary.is_base_form(next) \
                and dictionary.is_lexically_consistent(gram[:gram.index(next)]):
                    self.index = 0
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
                        self.index = 0
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
    
    def left_trim(self, gram):
        _indexes = [
            self.arrow.index,
            self.continuity.index,
            self.perfectivity.index
        ]
        indexes = [i for i in _indexes if i > -1]
        if not indexes:
            return gram
        return gram[min(indexes):]
        


#   Presents
class SimplePresent(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if len(gram) == 1 \
        and self.arrow(dictionary, gram) == 'present' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'SimplePresent'

class PresentPerfect(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'present' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PresentPerfect'

class PresentContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'present' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PresentContinuous'

class PresentPerfectContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'present' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PresentPerfectContinuous'


#   Pasts
class SimplePast(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if len(gram) == 1 \
        and self.arrow(dictionary, gram) == 'past' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'SimplePast'

class PastContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'past' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PastContinuous'

class PastPerfect(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'past' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PastPerfect'

class PastPerfectContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'past' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'PastPerfectContinuous'


# Futures
class SimpleFuture(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'future' \
        and not self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_base_form(gram[-1]) \
        and not [w for w in gram[:-1] if dictionary.is_base_form(w)]:
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'SimpleFuture'

class FutureContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'future' \
        and self.continuity(dictionary, gram) \
        and not self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'FutureContinuous'

class FuturePerfect(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'future' \
        and not self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_participle(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'FuturePerfect'

class FuturePerfectContinuous(VerbTense):
    def __call__(self, dictionary, tokens, start, end):
        gram = tokens[start:end]
        if self.arrow(dictionary, gram) == 'future' \
        and self.continuity(dictionary, gram) \
        and self.perfectivity(dictionary, gram) \
        and dictionary.is_gerund(gram[-1]):
            trimmed_gram = self.left_trim(gram)
            start += len(gram) - len(trimmed_gram)
            area = set(range(start, start + len(trimmed_gram)))
            return area, trimmed_gram
        return set([]), gram
    
    def name(self):
        return 'FuturePerfectContinuous'



class VerbTenseRecognizer:

    def __init__(self, min_gram=1, max_gram=6, verb_probs='verb.probabilities.bkp.csv'):
        self.verb_probs = verb_probs
        self.PoS = dict([])
        self.__load_probs()
        self.dictionary = FreelingDictionary(self.PoS)
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
    
    def __load_probs(self):
        if not os.path.exists(self.verb_probs):
            return
        for form, pos, prob in from_csv(self.verb_probs):
            if float(prob) < 0.33:
                continue
            if not self.PoS.has_key(form):
                self.PoS[form] = set([])
            self.PoS[form].add(pos)
    
    def __call__(self, tokens):
        matches = []
        covered = set([])
        for n in range(self.max_gram, self.min_gram - 1, -1):
            for i, gram in enumerate(ngrams(tokens, n)):
                for tense in self.tenses:
                    start = i
                    end = i + n
                    area, match = tense(self.dictionary, tokens, start, end)
                    if not area or area.intersection(covered):
                        continue
                    covered.update(area)
                    o = {
                        'start': min(area),
                        'end': max(area),
                        'text': ' '.join(match),
                        'tense': tense.name()
                    }
                    print gram, '\t', match, '\t', tense.name(), '\t'
                    matches.append(o)
                    break
        return matches
                        


# Training a model using NLTK for recognising tenses

#   for negatives verbs:
#       1. expand negative contractions
#       2. if negative, generate positive
#       3. check tense normally



if __name__ == '__main__':

    vtr = VerbTenseRecognizer()
    
    tests = [
#         'I study English every day.',
#         'I am studying English now.',
#         'I have studied English in several different countries.',
#         'I have been studying English for five years.',
#         'Two years ago, I studied English in England.',
#         'I was studying English when you called yesterday.',
#         'I had studied a little English before I moved to the U.S.',
#         'I had been studying English for five years before I moved to the U.S.',
#         'If you are having problems, I will help you study English.',
#         'I will be studying English when you arrive tonight.',
#         'I will have studied every tense by the time I finish this course.',
#         'I will have been studying English for over two hours by the time you arrive.',
#         
#         'I am going to study English next year.',    # exception!
#         'I am going to be studying English when you arrive tonight.',
#         'I am going to have studied every tense by the time I finish this course.',
#         'I am going to have been studying English for over two hours by the time you arrive.'
        'In fact , it could be as simple as planning a midnight stroll while the children are staying over with friends or relatives.',
        'In fact , it could be as simple as planning a midnight stroll while the children are actually staying over with friends or relatives.',
        'Ask the child to restate the rule. If children know a rule and are acting on impulse, ask them to stop what they are doing and identify the limit they are breaking. Tell them whether their description is correct.',
        'Show interest in what your child does. When you think children are about to misbehave, ask them to talk about what they are doing or what they have considered doing. This discussion might distract them from misbehavior.'
    ]
    for test in tests:
        tokens = tokenizer(test)
        if tokens:
            matches = vtr(tokens)
        if matches:
            print ' '.join(tokens)
            print json.dumps(matches, indent=4)
            print

    exit()
    umbc = UMBC()
    for par in umbc:
        tokens = []
        for token in par:
            if token.count('_') == 1:
                tokens.append(token.split('_')[0])
        if tokens:
            matches = vtr(tokens)
        if matches:
            print ' '.join(tokens)
            print json.dumps(matches, indent=4)
            print

    pyclean()
