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


class dataVisitor(lark.Visitor):
    def __init__(self):
        lark.Visitor.__init__(self)
        self.files = {}
        self.pages = {}
        self.page = 0

    def inputline(self, tree):
        inputtag = int(tree.children[0].children[0])
        filename = tree.children[1].strip()
        filename = filename.split("/./")[-1]
        assert inputtag not in files
        print(inputtag, filename)
        self.files[inputtag] = filename

    def sheet(self, tree):
        self.page += 1
        self.pages[self.page] = {}
        print("sheet")

    def _link(self, tree):
        self.cur_file = int(tree.children[0].children[0])
        self.cur_line = int(tree.children[1].children[0])

    def _handle_wh(self, tree):
        width = int(tree.children[0].children[0])
        height = int(tree.children[1].children[0])
        return (width, height)

    def _size(self, tree):
        self.cur_size = self._handle_wh(tree)
        #print("size {}".format(self.cur_size))

    def _point(self, tree):
        self.cur_point = tuple([int(x) for x in tree.children[0].children])
        #print("point {}".format(self.cur_point))

    def _shipout_box(self, cur_file, cur_line, cur_point, cur_size):
        pass

    def _out_box(self):
        '''
        Output a box to the underlying output system
        '''
        args = (self.cur_file, self.cur_line, self.cur_point, self.cur_size)
        self._shipout_box(*args)
        return args

#    def inputline(self, tree):
#        inputtag = int(tree.children[0].children[0])
#        filename = str(tree.children[1])
#        self.files[inputtag] = filename

    def vboxsection(self, tree):
        self._link(tree.children[0])
        self._point(tree.children[1])
        self._size(tree.children[2])
        if 0 not in self.cur_size:
            print("vboxsection {}".format(self._out_box()))

    def voidvboxrecord(self, tree):
        #print("voidvboxrecord {}".format(self._out_box()))
        pass

    def voidhboxrecord(self, tree):
        #print("voidhboxrecord {}".format(self._out_box()))
        pass

    def hboxsection(self, tree):
        #print("hboxsection {}".format(tree))
        self._link(tree.children[0])
        self._point(tree.children[1])
        self._size(tree.children[2])
        if 0 not in self.cur_size:
            print("hboxsection {}".format(self._out_box()))
        pass

    def NEWLINE(self, tree):
        print ("NEWLINE")

class annotationVisistor(dataVisitor):
    from pdf_annotate import PdfAnnotator, Location, Appearance

    def __init__(self):
        dataVisitor.__init__(self)
        self._annotator = self.PdfAnnotator("Textbausteintest.pdf") 
        self._page=0

    def sheet(self, tree):
        self._page += 1

    def _shipout_box(self, cur_file, cur_line, cur_point, cur_size):
        label = "{}:{}".format(self.files[cur_file], cur_line)
        cur_pos = [x/65535 for x in cur_point]
        cur_size = [x/65535 for x in cur_size]
        print(cur_pos, cur_size, self._page)
        self._annotator.add_annotation( 'square', self.Location(x1=cur_pos[1], y1=cur_pos[0], x2=cur_pos[0]+cur_size[0], y2=cur_pos[1]+cur_size[1], page=self._page), self.Appearance(stroke_color=(1, 0, 0), stroke_width=1),)
        """
        self._annotator.add_annotation("text",
                self.Location(x1=cur_point[0],y1=cur_point[1],x2=cur_point[0]+cur_size[0],y2=cur_point[1]+cur_size[1], page=self._page),
                self.Appearance(
                    fill=[0.4, 0, 0],
                    stroke_width=1,
                    font_size=5,r
                    content=label,
                ),
            )

        self._annotator.add_annotation( 'square',
                self.Location(x1=cur_point[0],y1=cur_point[1],x2=cur_point[0]+cur_size[0],y2=cur_point[1]+cur_size[1], page=self._page),
    self.Appearance(stroke_color=(1, 0, 0), stroke_width=5),
)

        self._annotator.add_annotation("ink",
                self.Location(points=[[cur_point[0],cur_point[1]],[cur_point[0]+cur_size[0],cur_point[1]+cur_size[1]]], page=self._page),
                self.Appearance(
                    stroke_color=(1,0,0),
                    stroke_width=1,
                ),
            )
        """
    def done(self):
        #self._annotator.add_annotation( 'square', self.Location(x1=50, y1=50, x2=100, y2=100, page=0), self.Appearance(stroke_color=(1, 0, 0), stroke_width=5),)
        self._annotator.write("out.pdf")


class cairoVisitor(dataVisitor):
    import cairo

    def __init__(self):
        dataVisitor.__init__(self)
        self._surface = self.cairo.PDFSurface("/tmp/x.pdf", 1000, 1000)
        self._ctx = self.cairo.Context(self._surface)
        # TeX coordinates to PDF?
        self._ctx.scale(1/65536., 1/65536.)


    def _shipout_box(self, cur_file, cur_line, cur_point, cur_size):
        self._ctx.rectangle(*cur_point, *cur_size)
        self._ctx.stroke()
        #self.cairo.select_font_face(self._ctx, "Sans", self.cairo.CAIRO_FONT_SLANT_NORMAL, self.cairo.CAIRO_FONT_WEIGHT_BOLD)
        #self.cairo.set_font_size(self._ctx, 100)
        self._ctx.move_to(*cur_point)
        self._ctx.set_font_size(65535*2)
        self._ctx.show_text("{}:{}".format(self.files[cur_file], cur_line))
        pass

    def sheet(self, tree):
        self._ctx.show_page()
        pass

# Dict inputtag -> filename
files = {}
# Dict {inputtag -> Dict { line -> (X,Y,W,H) } }
lines = {}

#pretty_print(data)
#process(data, files, lines)
v=annotationVisistor()
v.visit(data)
v.done()

#print(lines)
#with open("x", "wb") as f:
#    pickle.dump( {"files":files, "lines":lines} , f)
