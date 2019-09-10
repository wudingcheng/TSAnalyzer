import sys
sys.path.insert(0, "../")
from TSAnalyzer.models.reader import Reader
r = Reader()
r.readFile("cas1.dat")
print(r.df.head(5))
r.readFile("../Examples/CAND.sio.noamf_frame.pos")
print(r.df.head(5))