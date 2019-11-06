# coding: utf-8
import logging
import pickle
import lark

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


class dataVisitor(lark.Visitor):
    def __init__(self):
        lark.Visitor.__init__(self)
        self.files = {}
        self.pages = {}
        self.page = 0

    def inputline(self, tree):
        inputtag = tree.children[0].children[0].strip()
        filename = tree.children[1].strip()
        assert inputtag not in files
        self.files[inputtag] = filename

    def sheet(self, tree):
        self.page += 1
        self.pages[self.page] = {}
        print("sheet")

    def link(self, tree):
        self.cur_file = int(tree.children[0].children[0])
        self.cur_line = int(tree.children[1].children[0])

    def _handle_wh(self, tree):
        width = int(tree.children[0].children[0])
        height = int(tree.children[1].children[0])
        return (width, height)

    def size(self, tree):
        self.cur_size = self._handle_wh(tree)

    def point(self, tree):
        self.cur_point = tuple([int(x) for x in tree.children[0].children])

    def _out_box(self):
        return (self.cur_file, self.cur_line, self.cur_point, self.cur_size)

    def vboxsection(self, tree):
        print("vboxsection {}".format(self._out_box()))

    def voidvboxrecord(self, tree):
        print("voidvboxrecord {}".format(self._out_box()))

    def voidhboxrecord(self, tree):
        print("voidhboxrecord {}".format(self._out_box()))
        pass

    def hboxsection(self, tree):
        print("hboxsection {}".format(self._out_box()))
        pass

    def NEWLINE(self, tree):
        print ("NEWLINE")

# Dict inputtag -> filename
files = {}
# Dict {inputtag -> Dict { line -> (X,Y,W,H) } }
lines = {}

#pretty_print(data)
#process(data, files, lines)
dataVisitor().visit(data)

#print(lines)
#with open("x", "wb") as f:
#    pickle.dump( {"files":files, "lines":lines} , f)
