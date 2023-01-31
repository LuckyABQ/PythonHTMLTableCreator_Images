import re
import glob2
from PIL import Image, ImageDraw
import random
from typing import List, Dict
from collections import Counter
from bs4 import BeautifulSoup
from pathlib import Path
import os
import numpy as np
import itertools

from enum import Enum


class WritingType(Enum):
    def __str__(self):
        return '%s' % self.name

    HANDWRITING = 1
    SIGNATURE = 2


class ColorGenerator:

    def __init__(self, number_values: int = 8):
        step_width = int(240 / number_values)
        values = np.arange(10, 245 + step_width, step_width)
        self.colors = list(itertools.product(values, repeat=3))
        random.shuffle(self.colors)
        self.colors = [[int(i) for i in tup] for tup in self.colors]

    def get_color(self, counter):
        return self.colors[counter]


handwriting_root_path = \
    Path(r'data/handwriting_images/')

signatures_root_path = \
    Path(r'data/signatures/')

# todo: absolute path necessary for html
temp_images_path = \
    Path(r'/home/lukas/PycharmProjects/HTMLGeneration/PythonHtmlTableCreator/data/temp_images/')


class ImageProcessor:
    def __init__(self, probability_signatures: float = 0.5):
        self.images = {'handwritten': [], 'signatures': []}
        self.probability_signatures = probability_signatures
        self.counter_signatures = 0
        self.counter_handwriting = 0

        # preloading of handwriting images:
        # the text inside the images is only loaded, when needed
        self.paths_all_handwriting = [x for x in handwriting_root_path.rglob('*.png')]

        # load signatures
        suffixes = ['.png', '.PNG']
        self.paths_all_signature = [x for x in signatures_root_path.rglob('*') if x.suffix in suffixes]

        self.color_generator = ColorGenerator()

    def clean_up(self):
        """
        deletes all preloaded, and pre processed images that were created by this ImageProcessor
        :return: none
        """

        for signatures in self.images['signatures']:
            # get all paths
            original_image = signatures['path']
            color_box = original_image.replace("no_background", "color_box")
            binary = original_image.replace("no_background", "binary")

            # remove their files
            os.remove(original_image)
            os.remove(color_box)
            os.remove(binary)

        for handwritten in self.images['handwritten']:
            for original_image in handwritten['path']:
                # get all paths
                color_box = original_image.replace("no_background", "color_box")
                binary = original_image.replace("no_background", "binary")

                # remove their files
                os.remove(original_image)
                os.remove(color_box)
                os.remove(binary)






    @staticmethod
    def replace_image_with_boxes(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all('img'):
            img['src'] = img['src'].replace("no_background", "color_box")
        return soup.prettify()

    @staticmethod
    def replace_image_with_binaries(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all('img'):
            img['src'] = img['src'].replace("no_background", "binary")
        return soup.prettify()

    @staticmethod
    def normalize_with_beautifulsoup(html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.prettify()


    def get_next_image(self) -> Dict:
        """
        Preprocesses image for html usage
        :return: Dictionary containing path, name, writing_type. transform and if writing_type == handwriting, text
        """
        next_image = None
        if random.random() < self.probability_signatures:

            chosen_signature_file = random.choice(self.paths_all_signature)

            next_image = {'path': str(chosen_signature_file), 'name': chosen_signature_file.name,
                          'writing_type': str(WritingType.SIGNATURE)}
            self.counter_signatures += 1

            next_image['color'] = self.color_generator.get_color(self.counter_signatures)
            # make_white_area_transplant returns path for temporary file, with transparent background
            next_image['path'], next_image['shape'] = store_images_for_masks(next_image['path'], next_image['name'],
                                                                             box_color=next_image['color'])
            next_image['transform'] = get_rand_transform()


        else:
            content_counter = 0
            while content_counter < 3:
                chosen_handwriting_file = random.choice(self.paths_all_handwriting)
                next_image = {'path': str(chosen_handwriting_file), 'name': chosen_handwriting_file.name,
                              'writing_type': str(WritingType.HANDWRITING)}

                # determine name of xml file (for a01-000u-00-01 it is a01-000u, therefore split and join)
                xml_name = '-'.join(next_image['name'].split('-')[0:2])

                # open xml file and extract data
                with open(str(next(handwriting_root_path.rglob(xml_name + ".xml"))), 'r') as f:
                    data = f.read()

                # find the word in xml file, and its text
                soup = BeautifulSoup(data, "xml")
                current_object = soup.find(id=next_image['name'][:-4])
                next_image['path'] = []
                next_image['text'] = []
                next_image['name'] = []

                content_counter = 0

                while content_counter < 3:
                    if self.is_valid_handwriting(current_object['text']):
                        next_image['text'].append(current_object['text'])
                        next_image['path'].append(
                            str(list(handwriting_root_path.rglob(f"*{current_object['id']}*"))[0]))
                        next_image['name'].append(current_object['id'])
                        content_counter += 1
                    current_object = current_object.find_next('word')
                    if current_object.__eq__(None):
                        break
            new_paths = []
            new_colors = []
            new_shapes = []
            for (path, name) in zip(next_image['path'], next_image['name']):
                color = self.color_generator.get_color(self.counter_handwriting)
                self.counter_handwriting += 1
                current_path, current_shape = store_images_for_masks(path, name + ".png", color)
                new_paths.append(current_path)
                new_colors.append(color)
                new_shapes.append(current_shape)
            next_image['path'] = new_paths
            next_image['color'] = new_colors
            next_image['transform'] = get_rand_transform(scale=False)
            next_image['shape'] = new_shapes

        if next_image['writing_type'].__eq__(str(WritingType.SIGNATURE)):
            self.images['signatures'].append(next_image)
        else:
            self.images['handwritten'].append(next_image)
        return next_image

    def is_valid_handwriting(self, text: str) -> bool:
        return len(text) > 1 and re.search('[a-zA-Z]', text)


def get_rand_transform(scale: bool = True, rotation_max_degree: int = 30,
                       max_translationX_percentage: int = 20, max_translationY_percentage: int = 15) -> Dict:
    rotation = get_rand_rotation(rotation_max_degree)
    scale = get_rand_scale() if scale else 1
    result = {"rotation": rotation, "scale": scale,
              "translate": get_rand_translate(max_translationX_percentage, max_translationY_percentage)}
    return result


def get_rand_translate(max_translationX_percentage: int, max_translationY_percentage: int) -> str:
    translateX = random.uniform(-max_translationX_percentage, max_translationX_percentage)
    translateY = random.uniform(-max_translationY_percentage, max_translationY_percentage)
    return f"{translateX}%, {translateY}%"


def get_rand_rotation(rotation_max_degree: int) -> float:
    uniform_degree = rotation_max_degree / 4
    rotation = 0
    for i in range(0, 4),:
        rotation += random.uniform(- uniform_degree, uniform_degree)
    return rotation


def get_rand_scale() -> float:
    return 1 + abs(random.uniform(-0.5, 0.5))


def calc_transparency(background_grey: int, darkest_grey: int, grey_value: int) -> int:
    """
    Calculates transparency value for a given grey_value
    """

    linear_transparency = 255 - (grey_value - darkest_grey)

    # grey_value is 0 if pixel is black
    # alpha_chanel is 0 if fully transparent

    # pixel is almost white => set to transparent
    if grey_value > background_grey - 40:
        non_differentiable = 0

    else:
        non_differentiable = linear_transparency

    return non_differentiable


def store_images_for_masks(path: str, name: str, box_color: List[int]) -> str:
    """
     preprocessing of image: saves binary and semitransparent images in temp_images_path
     semi-transparent image: everything transparent except handwriting/signature
    :return: returns new path of semi-transparent image
    """
    with Image.open(path) as im:
        im = im.convert("RGBA")
        data_rgba = im.getdata()

        # grey_scale is used to determine how transparent a pixel should be
        image_grey = im.convert("L")
        data_grey = image_grey.getdata()

        transparent_data = []
        binary_data = []


        data_white = [item for item in data_grey if item > 125]

        set_data_grey = Counter(data_white)
        try:
            background_grey = set_data_grey.most_common(1)[0][0]
        except IndexError:
            print("IndexError: list index out of range with the image ", path)

        index_darkest_grey = np.argmin(data_grey)

        for item in zip(data_rgba, data_grey):
            transparency = calc_transparency(background_grey, data_grey[index_darkest_grey], item[1])
            transparent_data.append((data_rgba[index_darkest_grey][0], data_rgba[index_darkest_grey][0],
                                     data_rgba[index_darkest_grey][0], transparency))
            if transparency == 0:
                binary_data.append((0, 0, 0, 0))
            else:

                binary_data.append((255, 255, 255, 255))

        im.putdata(transparent_data)

        # save image without background
        output_path = temp_images_path / ("no_background_" + str(box_color) + "_" + name)
        bbox = im.getbbox()
        new_image = im.crop(bbox)
        new_image.save(output_path, "png")

        # save image as binary
        im.putdata(binary_data)
        new_image = im.crop(bbox)
        output_path_binary = temp_images_path / ("binary_" + str(box_color) + "_" + name)
        new_image.save(output_path_binary, "png")

        # is used to get bounding boxes
        size = new_image.size

        image_color_box = square_images(im, box_color, int(1 / 2 * min(size[0], size[1])))

        # save image as with color_box
        image_color_box = image_color_box.crop(bbox)
        output_path_box = temp_images_path / ("color_box_" + str(box_color) + "_" + name)
        image_color_box.save(output_path_box, "png")

    return str(output_path), new_image.size




def square_images(im: Image, color: List[int], square_size: int = 80) -> Image:
    # is used to get bounding boxes
    image_color_box = im.copy()
    image_color_box = image_color_box.convert("RGBA")

    # Get the width and height of the image
    height, width = image_color_box.size

    # Calculate the coordinates of the top-left corner of the square
    x1 = (width - square_size) // 2
    y1 = (height - square_size) // 2

    # Calculate the coordinates of the bottom-right corner of the square
    x2 = x1 + square_size
    y2 = y1 + square_size

    # Convert to array
    image_color_box_np = np.array(image_color_box)
    image_color_box_np[0:width, 0: height] = [0, 0, 0, 0]
    new_color = color.copy()
    new_color.append(255)
    image_color_box_np[x1: x2, y1: y2, :] = new_color

    image_color_box = Image.fromarray(image_color_box_np)

    return image_color_box
