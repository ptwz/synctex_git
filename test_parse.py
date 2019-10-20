# coding: utf-8
import x
import lark
import logging

logging.basicConfig(level=logging.DEBUG)


sa = lark.lark.Lark(open("./synctex.lark", "r"), debug=True)
with open("x.synctex", "r") as f:
    text = f.read()

    
print(sa.parse(text))
