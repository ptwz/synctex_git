# coding: utf-8
import lark
import logging
import pickle
import sys

logging.basicConfig(level=logging.DEBUG)


sa = lark.lark.Lark(open(sys.argv[1], "r"), debug=True)
with open("x.synctex", "r") as f:
    text = f.read()

    
parsed=sa.parse(text)

with open("tempfile", "wb") as f:
    pickle.dump(parsed, f)
