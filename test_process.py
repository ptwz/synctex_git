# coding: utf-8
import logging
import pickle

data = pickle.load(open("tempfile", "rb"))

def pretty_print(element, level=0):
    try:
        element.data
    except AttributeError:
        print("   "*level, "Terminal", element)
        return
    print("   "*level, element.data)
    for x in element.children:
        pretty_print(x, level+1)


def process(element, files, lines, level=0):
    try:
        data = element.data
    except AttributeError:
        return
    if data == 'inputline':
        inputtag = element.children[0].children[0].strip()
        filename = element.children[1].strip()
        print(inputtag, filename)
        assert inputtag not in files
        files[inputtag] = filename
    else:
        for child in element.children:
            process(child, files, lines, level+1)
# Dict inputtag -> filename
files = {}
# Dict {inputtag -> Dict { line -> (X,Y,W,H) } }
lines = {}

#pretty_print(data)
process(data, files, lines)
