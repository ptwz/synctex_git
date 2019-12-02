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
        self.files[inputtag] = filename
        self._input_file(inputtag, filename)

    def _input_file(self, inputtag, filename):
        '''
        When a new TeX input file was found, this stub
        is called. Use for own code in overlapping visitors
        '''
        pass

    def sheet(self, tree):
        '''
        Called when a page has been completely parsed.
        Takes the page number from the sheet record and
        stores in _page
        '''
        self._page = tree.children[1]

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
            self._out_box()

    def voidvboxrecord(self, tree):
        pass
        #print("voidvboxrecord {}".format(self._out_box()))

    def voidhboxrecord(self, tree):
        #print("voidhboxrecord {}".format(self._out_box()))
        pass

    def hboxsection(self, tree):
        #print("hboxsection {}".format(tree))
        self._link(tree.children[0])
        self._point(tree.children[1])
        self._size(tree.children[2])
        if 0 not in self.cur_size:
            #print("hboxsection {}".format(
            self._out_box()
            #)

    def NEWLINE(self, tree):
        print ("NEWLINE")

class annotationVisistor(dataVisitor):
    from pdf_annotate import PdfAnnotator, Location, Appearance
    from git import Repo, GitCommandError

    def __init__(self, repo):
        dataVisitor.__init__(self)
        self.repo = self.Repo(repo)
        self._annotator = self.PdfAnnotator("testdata/test.pdf")
        self._page=0
        self._blames = {}
        # List of annotations to drop onto a page once it
        # has finished
        self._annotations = []

    def sheet(self, tree):
        '''
        Render all our annotations on a page
        that has been finished.
        '''
        self._page = int(tree.children[1])
        for annot in self._annotations:
            # Patch page number, assuming all annotations have Location in 2nd
            # element
            annot[1].page = self._page - 1
            self._annotator.add_annotation(*annot)
        self._annotations = []

    def _input_file(self, inputtag, filename):
        try:
            #
            self.repo.blame("@", filename)
            self._blames[filename] = [x for x in self.repo.blame_incremental("@", filename)]
            logging.error("Can blame file {}".format(filename))
        except self.GitCommandError as e:
            self._blames[filename] = None

    def _shipout_box(self, cur_file, cur_line, cur_point, cur_size):
        # Create a label text for the current line
        filename = self.files[cur_file]
        assert filename in self._blames
        if self._blames[filename] is None:
            # Skip file when nothing to blame ;)
            return
        label = "{}:{}".format(self.files[cur_file], cur_line)
        print("Someone is to blame {}".format(label))

        cur_pos = [x/65535 for x in cur_point]
        cur_size = [x/65535 for x in cur_size]
        # Try to invert y position
        (px1,py1, px2,py2) = self._annotator.get_page_bounding_box(self._page-1)
        cur_pos[1] = py1 + py2 - cur_pos[1]

        # Draw a polygon around the box
        points = [[cur_pos[0],              cur_pos[1]],
                  [cur_pos[0]+cur_size[0],  cur_pos[1]],
                  [cur_pos[0]+cur_size[0],  cur_pos[1]+cur_size[1]],
                  [cur_pos[0],              cur_pos[1]+cur_size[1]],
                  ]
        self._annotations.append(
            ('polygon',
             self.Location(points=points, page=self._page),
             self.Appearance(fill=(1, 0, 0, 0.05), stroke_width=0)
             ))
        """
        self._annotations.append( ("text",self.Location(x1=cur_pos[1], y1=cur_pos[0], x2=cur_pos[0]+cur_size[0], y2=cur_pos[1]+cur_size[1], page=self._page) ,
                self.Appearance(
                    fill=[0.4, 0, 0],
                    stroke_width=1,
                    font_size=5,
                    content=label,
                ),
            ))
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
v=annotationVisistor(".")
v.visit(data)
v.done()

#print(lines)
#with open("x", "wb") as f:
#    pickle.dump( {"files":files, "lines":lines} , f)
