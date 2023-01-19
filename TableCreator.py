import random
import constants
import random as r
from html2image import Html2Image
import uuid
import os
import cv2
import re
from ImageProcessing import ImageProcessor

TAG_REGEX = r"#tag_([A-Za-z]+)_[0-9]+#"

REGULAR = 'regular'
TABLE = 'table'
TABLE_LINES = 'table_lines'
CELL = 'cell'
HANDWRITING = 'handwriting'
SIGNATURES = 'signatures'


class TableCreator:

    def __init__(self, html_template='templates/index.html', size=(1500, 2200), min_max_div=(1000, 1200),
                 table_line_color_paras=(0, 50, 0.7, 1.0), table_line_width=(1, 4), table_font_size=(16, 25),
                 text_color_paras=(0, 50, 0.7, 1.0), table_min_max_columns=(2, 7), table_text_length=(10, 20),
                 table_min_max_rows=(2, 7), table_min_max_lines_in_row=(1, 2), div_font_size=(20, 30),
                 text_min_max_length=(200, 2000), div_top_margin=(5, 100),
                 head_line_text_length=(50, 150), head_line_margin_top=(5, 10), head_line_margin_bottom=(5, 30),
                 head_line_font_size=(25, 55), head_line_text_alignment=['center', 'left', 'right'],
                 border_radius_min_max=(0, 10), line_types=['solid'],
                 collapse_types=['collapse'], table_text_alignment=['center', 'left', 'right'],
                 text_alignment=['center', 'left', 'right'], table_float_alignment=['left', 'right'],
                 float_alignment=['left', 'right'], contains_handwriting: bool = False):

        self.html_template = html_template
        self.size = size
        self.min_max_div = min_max_div
        self.table_line_color_paras = table_line_color_paras
        self.table_line_width = table_line_width
        self.table_font_size = table_font_size
        self.table_text_length = table_text_length
        self.table_min_max_rows = table_min_max_rows
        self.table_min_max_columns = table_min_max_columns
        self.table_min_max_lines_in_row = table_min_max_lines_in_row
        self.text_color_paras = text_color_paras
        self.div_font_size = div_font_size
        self.text_min_max_length = text_min_max_length
        self.div_top_margin = div_top_margin
        self.border_radius_min_max = border_radius_min_max
        self.line_types = line_types
        self.collapse_types = collapse_types
        self.table_text_alignment = table_text_alignment
        self.text_alignment = text_alignment
        self.table_float_alignment = table_float_alignment
        self.float_alignment = float_alignment
        self.head_line_text_length = head_line_text_length
        self.head_line_margin_top = head_line_margin_top
        self.head_line_margin_bottom = head_line_margin_bottom
        self.head_line_font_size = head_line_font_size
        self.head_line_text_alignment = head_line_text_alignment
        self.contains_handwriting = contains_handwriting
        if self.contains_handwriting:
            self.image_processor = ImageProcessor()

    def load_template(self):
        """generate image based on your template and parameters.
        returns the images in a json object:
        {'regular': regular_img, 'table': table_img, 'table_lines': table_lines_img, 'cell': cell_img}
        regular = the regular image of the html doc
        table = everything is black (0,0,0) but the table is one white (255,255,255) block
        table_lines = everything is black (0,0,0) but the table lines are white (255,255,255)
        cell = everything is black (0,0,0) but the table cells are white (255,255,255)
        """
        with open(self.html_template, 'r') as file:
            html = file.read().replace('\n', '')

        html = self.set_background(html)
        tags = self.get_replaceable_tags(html)

        for tag in tags:

            if tag['type'] == 'random':
                types = ['table', 'text', 'headline']
                tag['type'] = types[r.randrange(0, len(types))]

            if tag['type'] == 'table':
                html = self.generate_table(tag['name'], html)
            elif tag['type'] == 'text':
                html = self.generate_div_element(tag['name'], html)
            elif tag['type'] == 'headline':
                html = self.replace_headline(tag['name'], html)

        return self.generate_images_from_html(html)

    def get_replaceable_tags(self, html):
        """finds the replaceable tags within the html string.
        the tags follow the pattern #tag_keyword_number# e.g. #tag_random_0#, #tag_text_0#, #tag_headline_8#,
        #tag_table_0#"""
        tags = []
        matches = re.finditer(TAG_REGEX, html, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            for group_num in range(0, len(match.groups())):
                group_num = group_num + 1
                tags.append({'name': match.group(), 'type': match.group(group_num)})

        return tags

    def get_cell_html(self, html):
        """turns everything black but the cells white"""
        div_style = "h1, h2, h3, h4, h5, span, div {color: transparent !important;}"
        body_style = "body {color: transparent !important; background: black !important}"
        table_style = "table, tr, th, td {color: transparent !important;" \
                      "border-color: black !important;border-style: solid !important}"
        cell_style = "th, td {background-color: white !important;border-color: black !important;" \
                     "border-style: solid !important;}"
        img_style = "img{opacity: 0.0}"
        return html.replace('/*#custom*/', f'{div_style} {body_style} {table_style} {cell_style} {img_style}')

    def get_table_lines_html(self, html):
        """turns everything black but the table lines white"""
        div_style = "h1, h2, h3, h4, h5, span, div {color: transparent !important;}"
        body_style = "body {color: transparent !important; background: black !important}"
        table_style = "table, tr, th, td {color: transparent !important; border-color: white !important; " \
                      "border-style: solid !important}"
        img_style = "img{opacity: 0.0}"
        return html.replace('/*#custom*/', f'{div_style} {body_style} {table_style} {img_style}')

    def get_table_html(self, html):
        """turns everything black but the table as a block white"""
        div_style = "h1, h2, h3, h4, h5, span, div {color: transparent !important;}"
        body_style = "body {color: transparent !important; background: black !important}"
        table_style = "table, tr, th, td {color: transparent !important; border-color: white !important; " \
                      "border-style: solid !important; background: white !important}"
        return html.replace('/*#custom*/', f'{div_style} {body_style} {table_style}')

    def get_handwritten_html(self, html):
        """turns everything black but the handwritten images"""
        div_style = "h1, h2, h3, h4, h5, span, div {color: transparent !important;}"
        body_style = "body {color: transparent !important; background: black !important}"
        table_style = "table, tr, th, td {color: transparent !important;" \
                      "border-color: black !important;border-style: solid !important}"
        signature_style = ".SIGNATURE {opacity: 0.0;}"
        return html.replace('/*#custom*/', f'{div_style} {body_style} {table_style} {signature_style}')

    def get_signatures_html(self, html):
        """turns everything black but the handwritten images"""
        div_style = "h1, h2, h3, h4, h5, span, div {color: transparent !important;}"
        body_style = "body {color: transparent !important; background: black !important}"
        table_style = "table, tr, th, td {color: transparent !important;" \
                      "border-color: black !important;border-style: solid !important}"
        signature_style = ".HANDWRITING {opacity: 0.0;}"
        return html.replace('/*#custom*/', f'{div_style} {body_style} {table_style} {signature_style}')


    # todo: get_handwritten_boxes

    # todo: get_printed_boxes

    # todo: get_signature_boxes

    #todo: get_signatures_binary, printed_binary, handwritten_binary

    def generate_images_from_html(self, html):
        """render the html string (chromium) and return a numpy array for each"""

        hti = Html2Image()
        prefix = uuid.uuid4()
        html_cell = self.get_cell_html(html)
        html_table = self.get_table_html(html)
        html_table_lines = self.get_table_lines_html(html)

        html_image_binaries = self.image_processor.replace_image_with_binaries(html)

        html_handwritten = self.get_handwritten_html(html_image_binaries)
        html_signatures = self.get_signatures_html(html_image_binaries)


        hti.output_path = "temp_html"
        hti.screenshot(html_str=html, save_as=f'{prefix}_regular.png', size=self.size)
        hti.screenshot(html_str=html_table, save_as=f'{prefix}_table.png', size=self.size)
        hti.screenshot(html_str=html_table_lines, save_as=f'{prefix}_table_lines.png', size=self.size)
        hti.screenshot(html_str=html_cell, save_as=f'{prefix}_cell.png', size=self.size)
        hti.screenshot(html_str=html_handwritten, save_as=f'{prefix}_handwritten.png', size=self.size)
        hti.screenshot(html_str=html_signatures, save_as=f'{prefix}_signatures.png', size=self.size)
        # todo: save screenshot of printed,handwritten,signature_boxes

        with open("temp_html/temp_html_regular.html", "w") as text_file:
            text_file.write(html)

        regular_img = cv2.imread(f'temp_html/{prefix}_regular.png')
        table_img = cv2.imread(f'temp_html/{prefix}_table.png')
        table_lines_img = cv2.imread(f'temp_html/{prefix}_table_lines.png')
        cell_img = cv2.imread(f'temp_html/{prefix}_cell.png')
        handwritten_img = cv2.imread(f'temp_html/{prefix}_handwritten.png')
        signature_img = cv2.imread(f'temp_html/{prefix}_signatures.png')
        # todo: call imread

        self.clean_up(prefix)

        return {REGULAR: regular_img, TABLE: table_img, TABLE_LINES: table_lines_img,
                CELL: cell_img, HANDWRITING: handwritten_img, SIGNATURES: signature_img}, prefix

    def clean_up(self, prefix):
        """delete temp. created images from filesystem"""

        os.remove(f'temp_html/{prefix}_regular.png')
        os.remove(f'temp_html/{prefix}_table.png')
        os.remove(f'temp_html/{prefix}_table_lines.png')
        os.remove(f'temp_html/{prefix}_cell.png')
        # todo: remove other temp files

    def replace_headline(self, tag: str, html: str):
        """generates a random <h1> headline and replaces the given tag in the html string before it is returned"""
        random_text = self.get_random_text(*self.head_line_text_length)
        font_size = self.get_random_font_size(*self.head_line_font_size)
        font_weight = self.get_random_font_weight()
        align = self.get_random_text_align(self.head_line_text_alignment)
        font = self.get_random_font_family()
        margin_top = self.random_margin_top(*self.head_line_margin_top)
        margin_bottom = self.random_margin_top(*self.head_line_margin_bottom)
        color = self.get_random_color(*self.text_color_paras)
        h1 = f'<h1 style="{color}{font_size}{font_weight}{align}{margin_top}{margin_bottom}{font}">{random_text}</h1>'
        return html.replace(tag, h1)

    # todo: div elements with handwritten images?
    def generate_div_element(self, tag: str, html: str):
        """generates a random div element filled with text and replaces the
        given tag in the html string before it is returned"""

        # get random style
        width = f'width: {r.randrange(*self.min_max_div)}px;'
        color = self.get_random_color(*self.text_color_paras)
        font = self.get_random_font_family()
        font_size = self.get_random_font_size(*self.div_font_size)
        font_weight = self.get_random_font_weight()
        margin = self.random_margin_top(*self.div_top_margin)
        align = self.get_random_text_align(self.text_alignment)
        float_alignment = self.float_align(self.float_alignment)
        text = self.get_random_text(*self.text_min_max_length)


        # create styled div
        div = f'<div class="print" style="{color}{align}{width}{float_alignment}{font_size}{font_weight}{margin}{font}">{text}</div>'

        return html.replace(tag, div)

    def get_cell_text_and_style(self) -> str:
        text = self.get_random_text(*self.table_text_length)
        font = self.get_random_font_family()
        color = self.get_random_color(*self.text_color_paras)
        font_size = self.get_random_font_size(*self.table_font_size)
        font_weight = self.get_random_font_weight()
        align = self.get_random_text_align(self.table_text_alignment)

        return f'{color}{font_size}{font_weight}{font}{align}">{text}'

    def generate_table(self, tag: str, html: str):
        """generates a random table element and replaces the
        given tag in the html string before it is returned"""

        # get random style
        width = f'width: {r.randrange(*self.min_max_div)}px;'
        style = self.border_style_table()
        border_radius = self.random_border_radius()
        float_alignment = self.float_align(self.table_float_alignment)
        margin = self.random_margin_top(5, 10)
        bottom = self.random_margin_bottom(2, 10)
        margin_right = self.random_margin_right(2, 10)

        table = f'<table style="{style}{width}{float_alignment}{margin}{margin_right}{bottom}{border_radius}; position: relative;">'

        column_count = r.randrange(*self.table_min_max_columns)

        table += f'<tr style="{style}">'

        for column in range(column_count):
            # create header <th> elements
            table_cell_text = self.get_cell_text_and_style()

            border_style = self.border_style_table()
            table += f'<th style      ="{border_style}{table_cell_text}</th>'

        table += "</tr>"

        for row in range(r.randrange(*self.table_min_max_rows)):
            # create row <tr> elements
            style = self.border_style_table()
            color = self.get_random_color(*self.text_color_paras)
            table += f'<tr style="{style}">'

            for column in range(column_count):
                # create <td> elements
                divs = ""

                if self.contains_handwriting and random.uniform(0,1) > 0.33:
                    for cellText in range(r.randrange(*self.table_min_max_lines_in_row)):
                        next_image = self.image_processor.get_next_image()
                        divs += f'<div style="{next_image["transform"]}; width: fit-content; height: fit-content;' \
                                f' position: relative; z-index: -1;" > '

                        if next_image["writing_type"] == "HANDWRITING":
                            for (path, text) in zip(next_image['path'], next_image['text']):
                                divs += f'<img height=25 width="auto" src="{path}" ' \
                                        f'class="{str(next_image["writing_type"])}" ' \
                                        f'alt="{text}"> '
                        else:
                            divs += f'<img height=60 width=180 src="{next_image["path"]}" ' \
                                    f'class="{str(next_image["writing_type"])}" ' \
                                    f'alt="{next_image["name"]}">'
                        divs += f' </div>'
                    table += f'<td style="{style}{color};text-align:center; position: relative">{divs}</td>'
                else:
                    for cellText in range(r.randrange(*self.table_min_max_lines_in_row)):
                        # create <div> elements in each table cell for controlled multiline entries
                        table_cell_text = self.get_cell_text_and_style()

                        divs += f'<div class="print" style="{table_cell_text}</div>'
                    table += f'<td style="{style}{color}">{divs}</td>'

            table += "</tr>"
        table += "</table>"

        return html.replace(tag, table)

    def set_background(self, html: str):
        """sets the background of the html document randomly.
        there is a chance that the background is just a gradient or an image from the 'background' folder.
        this functionality works only if there is the '/*#bodyStyle*/'
        placeholder inside a style tag of your html template.
        if you want more/other background images,
        just place them in the 'backgrounds' folder"""

        val = r.randrange(0, len(constants.backgrounds) + 5)

        gradient = f'linear-gradient({r.randrange(0, 360)}deg, {self.get_random_black(170, 255, 0.0, 0.3)}, {self.get_random_black(150, 255, 0.8, 0.9)})'

        if val >= len(constants.backgrounds):
            # set basic color and gradient
            background = f"background-color: white; background-image: {gradient};"
        else:
            # set image and gradient
            img = constants.backgrounds[val].replace('\\', '/')
            background = f'background-image: {gradient}, url(\'{img}\');'

        return html.replace('/*#bodyStyle*/', f'{background}')

    def get_random_text(self, min: int, max: int):
        """gets a random part from the lorem impsum. The length of this text will be between your min and max,
        min is inclusive, max is exclusive"""
        start = r.randrange(0, len(constants.lorem) - 1 - max)
        end = r.randrange(start + min, start + max)

        return constants.lorem[start:end]


    def get_random_font_size(self, min: int, max: int):
        """gets a random font size between your min and max,
                min is inclusive, max is exclusive"""
        return f'font-size: {r.randrange(min, max)}px;'

    def get_random_font_weight(self):
        """returns randomly a font-weight of 'normal', 'bold' or 'bolder'"""
        weight = ['normal', 'bold', 'bolder']
        return f'font-weight: {weight[r.randrange(0, 3)]};'

    def get_random_text_align(self, alignment_list):
        """returns randomly the text-alignment, based on the passed list"""
        return f'text-align: {alignment_list[r.randrange(0, len(alignment_list))]};'

    def get_random_font_family(self):
        """returns a random font family"""
        font = constants.font_family[r.randrange(0, len(constants.font_family))]
        return f'font-family: {font};'

    def get_random_color(self, min: int, max: int, min_opacity: float, max_opacity: float):
        """returns a random rgba color attribute,
                     min is inclusive, max is exclusive"""
        return f'color: {self.get_random_rgba(min, max, min_opacity, max_opacity)};'

    def get_random_rgba(self, min: int, max: int, min_opacity: float, max_opacity: float):
        """returns a random rgba color (not an attribute),
                     min is inclusive, max is exclusive"""
        return f'rgba({r.randrange(min, max)},{r.randrange(min, max)},{r.randrange(min, max)},{r.uniform(min_opacity, max_opacity)})'

    def get_random_black(self, min: int, max: int, min_opacity: float, max_opacity: float):
        """returns a random gray scale color (not an attribute), this means rgb are random but r = g = b
                     min is inclusive, max is exclusive"""
        color = r.randrange(min, max)
        return f'rgba({color},{color},{color},{r.uniform(min_opacity, max_opacity)})'

    def border_style_table(self):
        """returns a random table or cell border style, based on the passed constructor values.
        check out the available styles https://www.w3schools.com/css/css_border.asp"""

        color = self.get_random_rgba(*self.table_line_color_paras)
        border_line = r.randrange(*self.table_line_width)

        border_line_type = self.line_types[r.randrange(0, len(self.line_types))]
        border_collapse = self.collapse_types[r.randrange(0, len(self.collapse_types))]

        style = f'border: {border_line}px {border_line_type} {color}; position: relative; border-collapse: {border_collapse}; '

        return style

    def random_margin_top(self, min: int, max: int):
        """returns a random top margin in px between your min and max,
                     min is inclusive, max is exclusive"""
        return f'margin-top: {r.randrange(min, max)}px;'

    def random_margin_right(self, min: int, max: int):
        """returns a random right margin in px between your min and max,
                     min is inclusive, max is exclusive"""
        return f'margin-right: {r.randrange(min, max)}px;'

    def random_margin_bottom(self, min: int, max: int):
        """returns a random bottom margin in px between your min and max,
                     min is inclusive, max is exclusive"""
        return f'margin-bottom: {r.randrange(min, max)}px;'

    def float_align(self, alignment_list):
        """returns a random float attribute based on the passed alignment_list"""
        return f'float: {alignment_list[r.randrange(0, len(alignment_list))]};'

    def random_border_radius(self):
        """returns a random border-radius"""
        border_radius = r.randrange(*self.border_radius_min_max)
        return f'border-radius: {border_radius}px;'