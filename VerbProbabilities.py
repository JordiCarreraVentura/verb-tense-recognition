
import os
import tqdm

from collections import (
    Counter,
    defaultdict as deft
)

from tqdm import tqdm

from Tools import (
    decode,
    encode,
    to_csv,
    pyclean
)


UMBC_PATH = '/Users/jordi/Laboratorio/corpora/raw/umbc/webbase_all/'

#   delorme.com_shu.pages_50.possf2


class UMBC:
    def __init__(self):
        self.files = [
            '%s%s' % (UMBC_PATH, f)
            for f in os.listdir(UMBC_PATH)
            if f.endswith('possf2')
        ]
    
    def __iter__(self):
        for f in self.files:
            print '\n', f
            with open(f, 'r') as rd:
                for line in tqdm(list(rd)):
                    l = decode(line).strip()
                    if l:
                        yield l.split()


class VerbProbabilities:

    def __init__(self):
        self.V = dict([])
        self.F = deft(Counter)
    
    def scan(self, umbc):
        for par in umbc:
            for token in par:
                try:
                    form, pos = token.split('_')
                    yield form.lower(), pos
                except Exception:
                    continue
    
    def find_verbs(self, umbc):
        for form, pos in self.scan(umbc):
            if pos.startswith('V'):
                self.V[form] = True
    
    def scan_pos_ambiguities(self, umbc):
        for form, pos in self.scan(umbc):
            if not self.V.has_key(form):
                continue
            self.F[form][pos] += 1
    
    def __iter__(self):
        for form in self.V.keys():
                yield form
    
    def __getitem__(self, v):
        return self.F[v].most_common()
    
    def is_ambiguous(self, form):
        if [pos for pos in self.F[form].keys() if not pos.startswith('V')]:
            return True
        return False
    
    def to_csv(self, out):
        data = []
        for v in self:
            if not self.is_ambiguous(v):
                data.append((encode(v), 'VB', 1.0))
            else:
                poses = {
                    'V': 0.0,
                    '*': 0.0
                }
                _data = self[v]
                if sum(zip(*_data)[1]) < 40:
                    continue
                for pos, freq in _data:
                    if pos.startswith('V'):
                        poses['V'] += freq
                    else:
                        poses['*'] += freq
                t = sum(poses.values())
                for pos, freq in sorted(
                    poses.items(), reverse=True, key=lambda x: x[1]
                ):
                    data.append((encode(v), pos, freq / t))
        to_csv(data, out)


if __name__ == '__main__':

    umbc = UMBC()
    
    vp = VerbProbabilities()
    
    vp.find_verbs(umbc)
    vp.scan_pos_ambiguities(umbc)
    
    vp.to_csv('verb.probabilities.csv')
    
    pyclean()
