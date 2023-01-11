from PIL import Image
import random
from typing import List, Dict
from collections import Counter
from bs4 import BeautifulSoup
from pathlib import Path
import os
import numpy as np

from enum import Enum


class WritingType(Enum):
    HANDWRITING = 1
    SIGNATURE = 2


handwriting_root_path = \
    Path(r'data/handwriting_images/')

signatures_root_path = \
    Path(r'data/signatures/')

# todo: absolute path necessary for html
temp_images_path = \
    Path(r'/home/lukas/PycharmProjects/HTMLGeneration/PythonHtmlTableCreator/data/temp_images/')


class ImageProcessor:
    def __init__(self, number_images: int = 200, probability_signatures: float = 0.5):
        self.signature = None
        self.handwriting = None
        self.number_images = number_images
        self.probability_signatures = probability_signatures
        self.counter_signatures = 0
        self.counter_handwriting = 0
        self.preload_images(number_images)
        self.clean_up()

    def clean_up(self):
        """
        deletes all preloaded, and pre processed images
        :return: none
        """
        removing_files = temp_images_path.glob('*.png')
        for r in removing_files:
            os.remove(r)

    def preload_images(self, number_images: int) -> None:
        """
        determines used images for next file - containing signatures and normal handwriting
        metadata stored in self.handwriting and self.signature
        :param number_images: loads number of images for each type, handwriting and signatures
        :return:
        """
        # for each preloaded image we need its absolute path (=source), its name,
        # and its writing_type (signature or handwriting)

        # preloading of handwriting images:
        # the text inside the images is only loaded, when needed
        all_handwriting_images = [x for x in handwriting_root_path.rglob('*.png')]
        chosen_handwriting_files = random.choices(all_handwriting_images, k=number_images)
        self.handwriting = [{'path': str(x), 'name': x.name, 'writing_type': str(WritingType.HANDWRITING)} for x in
                            chosen_handwriting_files]

        # load signatures
        suffixes = ['.png', '.PNG']
        all_signature_images = [x for x in signatures_root_path.rglob('*') if x.suffix in suffixes]
        chosen_signature_files = random.choices(all_signature_images, k=number_images)
        self.signature = [{'path': str(x), 'name': x.name, 'writing_type': str(WritingType.SIGNATURE)} for x in
                          chosen_signature_files]

    def get_next_image(self) -> (str, str, str, str, str):
        """
        Preprocesses image for html usage
        :return: Dictionary containing path, name, writing_type. transform and if writing_type == handwriting, text
        """
        next_image = None
        if random.random() < self.probability_signatures:
            next_image = self.signature[self.counter_signatures]
            self.counter_signatures += 1

        else:

            # some images contain just one element - which is considered not long enough
            is_long_enough = False

            while not is_long_enough:
                # get next image from handwriting list
                next_image = self.handwriting[self.counter_handwriting]
                self.counter_handwriting += 1

                # determine name of xml file (for a01-000u-00-01 it is a01-000u, therefore split and join)
                xml_name = '-'.join(next_image['name'].split('-')[0:2])

                # open xml file and extract data
                with open(str(next(handwriting_root_path.rglob(xml_name + ".xml"))), 'r') as f:
                    data = f.read()

                # find the word in xml file, and its text
                soup = BeautifulSoup(data, "xml")
                meta_data_word = soup.find(id=next_image['name'][:-4])
                next_image['text'] = meta_data_word['text']
                is_long_enough = len(next_image['text']) > 1

        next_image['transform'] = get_rand_transform()

        # make_white_area_transplant returns path for temporary file, with transparent background
        next_image['path'] = store_images_for_masks(next_image)

        return next_image


# todo: overlapping with table boarders
def get_rand_transform() -> str:
    transform = f"transform: translate({get_rand_translate()}) " \
                f"rotate({get_rand_rotation()}deg)"\
                f"{get_rand_scale()}"
    return transform


def get_rand_translate() -> str:
    # Translation: max one quarter of the image should overlap the table border
    translateX = random.uniform(-40, 40)
    translateY = random.uniform(-30, 30)
    return f"{translateX}%, {translateY}%"

def get_rand_rotation() -> float:
    # rotation of max +-30deg
    rotation = random.uniform(-20, 20)
    return rotation

def get_rand_scale() -> str:
    # Scaling of 0,9-1,1
    scale = 1 + (random.random() - 0.5) * 0.1
    return f"scale({scale})"


def calc_transparency(background_grey: int, darkest_grey: int, grey_value: int) -> int:
    """
    Calculates transparency value for a given grey_value
    """

    linear_transparency = 255 - (grey_value - darkest_grey)
    quadratic_transparency = int((linear_transparency / 255) ** 2 * 255)
    cubic_transparency = int((linear_transparency / 255) ** 3 * 255)
    quartic_transparency = int((linear_transparency / 255) ** 4 * 255)

    # grey_value is 0 if pixel is black
    # alpha_chanel is 0 if fully transparent

    # pixel is almost white => set to transparent
    if grey_value > background_grey - 40:
        non_differentiable = 0

    else:
        non_differentiable = linear_transparency

    # grey_value < darkest_grey - 30:

    return non_differentiable


def store_images_for_masks(next_image: Dict) -> str:
    """
     preprocessing of image: saves binary and semitransparent images in temp_images_path
     semi-transparent image: everything transparent except handwriting/signature
    :return: returns new path of semi-transparent image
    """
    im = Image.open(next_image['path'])
    im = im.convert("RGBA")
    data_rgba = im.getdata()

    # save not_transparent_image -> debugging
    # output_path = temp_images_path / ("not_transparent_" + next_image['name'])
    # im.save(output_path, "PNG")

    # grey_scale is used to determine how transparent a pixel should be
    image_grey = im.convert("L")
    data_grey = image_grey.getdata()

    transparent_data = []
    binary_data = []

    set_data_grey = Counter(data_grey)
    background_grey = set_data_grey.most_common(1)[0][0]
    index_darkest_grey = np.argmin(data_grey)
    for item in zip(data_rgba, data_grey):
        transparency = calc_transparency(background_grey, data_grey[index_darkest_grey], item[1])
        transparent_data.append((data_rgba[index_darkest_grey][0], data_rgba[index_darkest_grey][0],
                                 data_rgba[index_darkest_grey][0], transparency))
        if transparency == 0:
            binary_data.append((255, 255, 255, 255))
        else:

            binary_data.append((0, 0, 0, 255))

    im.putdata(transparent_data)

    # save image without background
    output_path = temp_images_path / ("no_background_" + next_image['name'])
    bbox = im.getbbox()
    new_image = im.crop(bbox)
    new_image.save(output_path, "PNG")

    # save image as binary
    im.putdata(binary_data)
    new_image = im.crop(bbox)
    output_path_binary = temp_images_path / ("binary_" + next_image['name'])
    new_image.save(output_path_binary, "PNG")

    return output_path


# Debugging: Transparency
"""suffixes = ['.png', '.PNG']
all_signature_images = [x for x in signatures_root_path.rglob('*') if x.suffix in suffixes]
chosen_signature_files = random.choices(all_signature_images, k=200)
signatures = [{'path': str(x), 'name': x.name, 'writing_type': str(WritingType.SIGNATURE)} for x in
              chosen_signature_files]
store_images_for_masks(signatures[1])"""
