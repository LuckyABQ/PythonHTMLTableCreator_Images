import json
import pathlib
from PIL import Image
import random
from typing import List, Dict
import uuid
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
    Path(r'/home/lukas/Documents/data/html_generation_data/handwriting')

signatures_root_path = \
    Path(r'/home/lukas/Documents/data/html_generation_data/signatures/no_background/')



class ImageProcessor:
    def __init__(self, probability_signatures: float = 0.5, has_offsets: bool = True):
        self.images = {'handwritten': [], 'signatures': []}
        self.probability_signatures = probability_signatures
        self.counter_signatures = 0
        self.counter_handwriting = 0
        self.handwriting_root_path = handwriting_root_path
        self.has_offsets = has_offsets

        # preloading of handwriting images:
        # the text inside the images is only loaded, when needed
        with open(f"{handwriting_root_path}/words.json") as f:
            self.paths_all_handwriting =json.load(f)


            # load signatures
        suffixes = ['.png', '.PNG']
        self.paths_all_signature = [x for x in signatures_root_path.rglob('*') if x.suffix in suffixes]

        self.color_generator = ColorGenerator()

    #needs refactoring
    def clean_up(self):
        """
        deletes all preloaded, and pre processed images that were created by this ImageProcessor
        :return: none
        """

        for signatures in self.images['signatures']:
            # get all paths
            original_image = signatures['path']
            color = signatures['color_string']
            color_box = original_image.replace("no_background/", f"color_box/{color}_")

            # remove their files
            os.remove(color_box)


        for handwritten in self.images['handwritten']:
            for (original_image, color) in zip(handwritten['path'], handwritten['color_string']):
                # get all paths
                color_box = original_image.replace("no_background/", f"color_box/{color}_")
                # remove their files
                os.remove(color_box)


    @staticmethod
    def replace_image_with_boxes(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all('img'):
            if 'data-color' in img:
                color = img['data-color']
                img['src'] = img['src'].replace("no_background/", f"color_box/{color}_")
            else:
                prefix = uuid.uuid4()
                with open(f"debug/{prefix}_debug.html", "w") as text_file:
                    text_file.write(html)

        return soup.prettify()

    @staticmethod
    def replace_image_with_binaries(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all('img'):
            img['src'] = img['src'].replace("no_background", f"binary")
        return soup.prettify()

    @staticmethod
    def normalize_with_beautifulsoup(html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.prettify()

    def get_three_hw_img_in_row(self):
        matching_row = False
        while not matching_row:
            index = random.randint(0, len(self.paths_all_handwriting))
            if index + 3 < len(self.paths_all_handwriting):
                elements = self.paths_all_handwriting[index: index + 3]
                if not int(elements[0]['name'].split("-")[-1]) + 1 == int(elements[1]['name'].split("-")[-1]):
                    continue
                if not int(elements[1]['name'].split("-")[-1]) + 1 == int(elements[2]['name'].split("-")[-1]):
                    continue

                matching_row = True
                next_images = {'path': [], 'text': [], 'name': []}
                for element in elements:
                    next_images['path'].append(f"{self.handwriting_root_path}/no_background/{element['name']}.png")
                    next_images['name'].append(element['name'])
                    next_images['text'].append(element['text'])
                    next_images['writing_type'] = str(WritingType.HANDWRITING)
        return next_images


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
            next_image['shape'] = produce_color_boxes(next_image['path'], next_image['name'],
                                                                             box_color=next_image['color'])
            next_image['transform'] = self.get_rand_transform()
            next_image['color_string'] = str(next_image['color'])


        else:
            next_image = self.get_three_hw_img_in_row()

            new_paths = []
            new_colors = []
            new_colors_string =[]
            new_shapes = []

            for (path, name) in zip(next_image['path'], next_image['name']):
                color = self.color_generator.get_color(self.counter_handwriting)
                self.counter_handwriting += 1
                current_shape = produce_color_boxes(path, name + ".png", color)
                new_paths.append(path)
                new_colors.append(color)
                new_colors_string.append(str(color))
                new_shapes.append(current_shape)
            next_image['path'] = new_paths
            next_image['color'] = new_colors
            next_image['transform'] = self.get_rand_transform(scale=False)
            next_image['shape'] = new_shapes
            next_image['color_string'] = new_colors_string

        if next_image['writing_type'].__eq__(str(WritingType.SIGNATURE)):
            self.images['signatures'].append(next_image)
        else:
            self.images['handwritten'].append(next_image)
        return next_image



    def get_rand_transform(self, scale: bool = True, rotation_max_degree: int = 30,
                           max_translationX_percentage: int = 20, max_translationY_percentage: int = 15) -> Dict:

        if self.has_offsets:
            rotation = get_rand_rotation(rotation_max_degree)
            scale = get_rand_scale() if scale else 1
            result = {"rotation": rotation, "scale": scale,
                      "translate": get_rand_translate(max_translationX_percentage, max_translationY_percentage)}
        else:
            result = {"rotation": 0, "scale": 1,"translate": f"0%, 0%"}
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


def produce_color_boxes(path: str, name: str, box_color: List[int]):
    with Image.open(path) as im:
        im = im.convert("RGBA")

        # is used to get bounding boxes
        size = im.size

        image_color_box = square_images(im, box_color, int(1 / 2 * min(size[0], size[1])))


        pathlib_path = pathlib.Path(path)
        # save image as with color_box
        output_path_box = pathlib_path.parent.parent / ("color_box/" + str(box_color) + "_" + name)

        image_color_box.save(output_path_box, "png")
    return size


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
