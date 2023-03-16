import TableCreator
import cv2
import os
import json


def write(images, overlay_image, boxes, prefix, folder='generate'):
    """write all images and json files"""

    cv2.imwrite(f'{folder}/doc/{prefix}.jpg', images[TableCreator.REGULAR])
    cv2.imwrite(f'{folder}/mask_cell/{prefix}.png', images[TableCreator.CELL])
    cv2.imwrite(f'{folder}/mask_table/{prefix}.png', images[TableCreator.TABLE])
    cv2.imwrite(f'{folder}/mask_table_line/{prefix}.png', images[TableCreator.TABLE_LINES])
    cv2.imwrite(f'{folder}/mask_handwriting/{prefix}.png', images[TableCreator.HANDWRITING])
    cv2.imwrite(f'{folder}/mask_print/{prefix}.png', images[TableCreator.PRINT])
    cv2.imwrite(f'{folder}/mask_signature/{prefix}.png', images[TableCreator.SIGNATURES])
    cv2.imwrite(f'{folder}/overlay/{prefix}.jpg', overlay_image)

    with open(f'{folder}/box/{prefix}.json', 'w', encoding='utf-8') as f:
        json.dump(boxes, f, ensure_ascii=False, indent=4)



def delete_all(folder='generate'):
    """delete all files recursively (not folders)"""
    for path in os.listdir(folder):
        full_path = f"{folder}/" + path
        if os.path.isdir(full_path):
            delete_all(full_path)
        else:
            os.remove(full_path)


def make_folders(folder):
    """creates all folders to store the table data"""

    create_if_not_exists(folder)
    create_if_not_exists(f'{folder}/doc')
    create_if_not_exists(f'{folder}/box')
    create_if_not_exists(f'{folder}/mask_cell')
    create_if_not_exists(f'{folder}/mask_table')
    create_if_not_exists(f'{folder}/mask_table_line')
    create_if_not_exists(f'{folder}/mask_handwriting')
    create_if_not_exists(f'{folder}/mask_print')
    create_if_not_exists(f'{folder}/mask_signature')
    create_if_not_exists(f'{folder}/overlay')


def create_if_not_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
