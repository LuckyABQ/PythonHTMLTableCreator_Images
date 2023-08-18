import json
from pathlib import Path
from PIL import Image
import numpy as np
from collections import Counter
from tqdm import tqdm
import os
import re



signatures_root_path = \
    Path(r'data/signatures_old/')


def prepare_signatures():
    suffixes = ['.png', '.PNG']
    result_path = "/home/lukas/Documents/data/html_generation_data/signatures"
    all_signatures_list = [signature for signature in signatures_root_path.rglob('*') if signature.suffix in suffixes]
    for i in tqdm(range(len(all_signatures_list))):
        name = all_signatures_list[i].name
        already_there = os.path.isfile(result_path + ("/no_background/" + name + ".png")) and \
                        os.path.isfile(result_path + ("/binary/" + name + ".png"))
        if not already_there:
            store_images_for_masks(source_path=str(all_signatures_list[i]), result_path=result_path, name=name)


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


def store_images_for_masks(source_path: str, result_path: str,  name: str) -> int:
    """
     preprocessing of image: saves binary and semitransparent images in temp_images_path
     semi-transparent image: everything transparent except handwriting/signature
    :return: returns new path of semi-transparent image
    """
    try:
        with Image.open(source_path) as im:
            im = im.convert("RGBA")
            data_rgba = im.getdata()

            # grey_scale is used to determine how transparent a pixel should be
            image_grey = im.convert("L")
            data_grey = image_grey.getdata()

            transparent_data = []
            binary_data = []

            data_white = [item for item in data_grey if item > 125]

            set_data_grey = Counter(data_white)
            background_grey = set_data_grey.most_common(1)[0][0]

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
            output_path = result_path + ("/no_background/" + name + ".png")
            bbox = im.getbbox()
            new_image = im.crop(bbox)
            new_image.save(output_path, "png")

            # save image as binary
            im.putdata(binary_data)
            new_image = im.crop(bbox)
            output_path_binary = result_path + ("/binary/" + name + ".png")
            new_image.save(output_path_binary, "png")

        return 1

    except:
        return 0


def prepare_iam():
    path_ascii = "/home/lukas/Documents/data/html_generation_data/handwriting/words.txt"
    path_image_source = "/home/lukas/PycharmProjects/HTMLGeneration/PythonHtmlTableCreator/data/handwriting_images_old/words"
    result_path = "/home/lukas/Documents/data/html_generation_data/handwriting"

    images = []
    with open(path_ascii) as f:
        lines = f.readlines()

    for i in tqdm(range(len(lines))):
        line = lines[i]
        if not line[0] == "#":
            split_line = line.split(" ")
            if len(split_line) == 9 and split_line[1] == "ok":
                file_name = split_line[0]
                text = split_line[-1]
                file_name_split = file_name.split("-")

                file_path = f"{path_image_source}/no_background/{file_name}.png"
                status = store_images_for_masks(source_path=file_path, result_path=result_path, name=file_name)
                file_dict={}
                file_dict['name'] = file_name
                file_dict['text'] = text

                if status:
                    images.append(file_dict)

    with open(f"/home/lukas/PycharmProjects/HTMLGeneration/PythonHtmlTableCreator/data/handwriting/words.json", "w") as outfile:
        json.dump(images, outfile)


def is_valid_handwriting(text: str) -> bool:
    return len(text) > 1 and re.search('[a-zA-Z]', text)


def fix_iam():
    path_ascii = "/home/lukas/Documents/data/html_generation_data/handwriting/words.txt"
    result_path = "/home/lukas/Documents/data/html_generation_data/handwriting"

    images = []
    with open(path_ascii) as f:
        lines = f.readlines()

    for i in tqdm(range(len(lines))):
        line = lines[i]
        if not line[0] == "#":
            split_line = line.split(" ")
            if len(split_line) == 9 and split_line[1] == "ok":
                file_name = split_line[0]
                text = split_line[-1]
                file_name_split = file_name.split("-")

                file_path = f"{result_path}/binary/{file_name}.png"
                file_dict={}
                file_dict['name'] = file_name
                file_dict['text'] = text

                if os.path.isfile(file_path) and is_valid_handwriting(file_dict['text']):
                    images.append(file_dict)

    with open(f"{result_path}/words.json", "w") as outfile:
        json.dump(images, outfile)

