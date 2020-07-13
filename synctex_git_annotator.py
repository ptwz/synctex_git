# coding: utf-8
import lark
import logging
import sys
from os.path import splitext

from process import annotationVisistor

logging.basicConfig(level=logging.DEBUG)

sa = lark.lark.Lark(open("synctex.lark", "r"))

pdf_name = sys.argv[1]
base_name = splitext(pdf_name)[0]
synctex_name = base_name+".synctex"
print(f"pdf_name={pdf_name}, base_name={base_name}, synctex_name={synctex_name}")
with open(synctex_name, "r") as f:
    text = f.read()

tree = sa.parse(text)

v = annotationVisistor(".")

v.visit(tree)
v.done()
