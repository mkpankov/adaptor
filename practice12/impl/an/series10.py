# coding: utf-8
f = open('series10.csv')
S = f.read()
samples = S.splitlines()
len(samples)
del samples[0]
len(samples)
times = [x[2] for x in samples]
times[0]
samples
fields = [x.split('\t') for x in samples]
times = [x[2] for x in fields]
times[0]
times[1]
fields[:][:2][0]
fields[:][:2]
fields1 = [x[:2] + x[4:] for x in fields]
fields1[0]
fields1 = [x[:2] + x[3:] for x in fields]
fields1[0]
len(fields1)
len(fields1[0])
f.seek(0)
fields1 = [x[3:] for x in fields]
fields2 = [convert(y) for x in fields1 for y in x]
def convert(x):
    try:
        x = int(x)
    except ValueError:
        try:
            x = float(x)
        except ValueError:
            if x == 'True':
                x = True
            elif x == 'False':
                x = False
            else:
                x = str(x)
   return x
def convert(x):
    try:
        x = int(x)
    except ValueError:
        try:
            x = float(x)
        except ValueError:
            if x == 'True':
                x = True
            elif x == 'False':
                x = False
            else:
                x = str(x)
    return x
convert('1234')
convert('1234.56')
convert('True')
convert('False')
convert('dqk')
fields2 = [convert(y) for x in fields1 for y in x]
fields2[0]
fields2[1]
fields1 = [x[7:] for x in fields]
x[0][0]
x[0]
fields1[0][0]
fields2 = [convert(y) for x in fields1 for y in x]
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction import DictVectorizer
import sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction import text
get_ipython().magic(u'pinfo text')
get_ipython().magic(u'save')