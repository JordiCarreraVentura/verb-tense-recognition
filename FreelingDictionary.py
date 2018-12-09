import tqdm

from collections import defaultdict as deft

from tqdm import tqdm



def read(f):
    rows = []
    with open(f, 'r') as rd:
        for l in tqdm(list(rd)):
            row = l.strip().split()
            rows.append(row)
    return rows


BREAKER_EXCEPTIONS = [
    ('have', 'have', 'JJ')
]


class FreelingDictionary:
    
    def __init__(self):
        self.contractions = []
        self.determiners = []
        self.adverbs = []
        self.breakers = deft(bool)
        self.forms_by_lemma = deft(dict)
        self.lemmas_by_form = deft(list)
        self.__load()

    def to_be(self, w):
        if self._to_be.has_key(w):
            return self._to_be[w]
        return None
    
    def __load_adverbs(self):
        self.adverbs = deft(bool)
        for form, lemma, pos in read('dictionary/adv'):
            self.adverbs[lemma] = True
    
    def __to_be(self):
        self._to_be = {
            form: pos
            for form, lemma, pos in read('dictionary/verbs.aux')
            if lemma == 'be'
        }
    
    def __getitem__(self, w):
        if not self.lemmas_by_form.has_key(w):
            return []
        return [lemma for lemma in self.lemmas_by_form[w]]
        
    def is_past(self, w):
        lemmas = self[w]
        for lemma in lemmas:
            if 'VBD' in self.forms_by_lemma[lemma][w]:
                return True
        return False
        
    def is_present(self, w):
        lemmas = self[w]
        for lemma in lemmas:
            if set(self.forms_by_lemma[lemma][w]).intersection(
                set(['VBP', 'VBZ'])
            ):
                return True
        return False
    
    def is_base_form(self, w):
        lemmas = self[w]
        for lemma in lemmas:
            if 'VB' in self.forms_by_lemma[lemma][w]:
                return True
        return False
        
    def is_gerund(self, w):
        lemmas = self[w]
        for lemma in lemmas:
            if 'VBG' in self.forms_by_lemma[lemma][w]:
                return True
        return False
    
    def is_finite_verb(self, w):
        lemmas = self[w]
        for lemma in lemmas:
            if set(self.forms_by_lemma[lemma][w]).intersection(
                set(['VBP', 'VBZ', 'VBD'])
            ):
                return True
        return False

    def __load(self):
        self.__to_be()
        self.__load_verbs()
        self.__load_adverbs()
        self.__load_breakers()
    
    def __load_verbs(self):
        verbs = read('dictionary/verbs') + read('dictionary/verbs.aux')
        for form, lemma, pos in tqdm(verbs):
            if not self.forms_by_lemma[lemma].has_key(form):
                self.forms_by_lemma[lemma][form] = []
            self.forms_by_lemma[lemma][form].append(pos)
            self.lemmas_by_form[form].append(lemma)
    
    def is_lexically_consistent(self, gram):
        if [w for w in gram[1:-1] if self.breakers[w]]:
            return False
        return True

    def __load_breakers(self):
        for f in [
            'dictionary/tanc',
            'dictionary/numerals.dat',
            'dictionary/numbers.DT',
            'dictionary/interj',
            'dictionary/adv.comp',
            'dictionary/adjs.comp',
            'dictionary/adjs'
        ]:
            rows = read(f)
            for form, lemma, pos in tqdm(rows):
                if (form, lemma, pos) in BREAKER_EXCEPTIONS:
                    continue
                self.breakers[form] = True
                
                # IMPORTANT NOTE (please keep!)
                # We can tolerate verb-(any-other-class) ambiguities
                # in the dictionary because detection will look at
                # verb-final word sequences (so, we're still focusing
                # on actual known verbs) and will only ignore them if
                # if a breaker appears between the auxiliary verb
                # introducing the current word sequence and the 
                # lexical verb closing the same sequence.
#                 if self.forms_by_lemma.has_key(lemma):
#                     print 'adj', form, lemma
#                     print 'verb', self.forms_by_lemma[lemma]

#        TODO: self.closed_class_adverbs = dict([])   # +everything ending in -ly
#        TODO: self.numerals = 
####        self.closed_class_prepositions = dict([])
####        self.closed_class_determiners = dict([])
