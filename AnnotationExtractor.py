import cv2
import numpy as np
import random


def get_table_annotations(table_mask):
    """calculates the boxes for the tables (entire table not the cells) and returns it as a numpy array and a list"""

    gray_mask = cv2.cvtColor(table_mask, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(gray_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    table_mask = np.zeros((table_mask.shape[0], table_mask.shape[1], 3)).astype(np.uint8)

    idx = 1
    boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # add coordinates for left top and right bottom corner of the rectangle
        box_data = {'xStart': x, 'yStart': y, 'xEnd': x + w, 'yEnd': y + h, 'color': idx}
        boxes.append(box_data)
        # draw rectangle to the numpy array, each rectangle with a different color
        # note that the "colors" are gray scale the background is black = 0 and the colors start with 1 and increasing
        # this means you can't really distinguish them
        cv2.drawContours(table_mask, contours, idx - 1, (idx, idx, idx), -1)

        idx += 1

    return table_mask, boxes


def get_cell_annotations(table_boxes, original_cell_mask, table_line_mask=None, image_to_overlay=None):
    """calculates the boxes for the cells based on the boxes for the table and returns it as a numpy array and a list.
    The list contains the boxes for the table and the cells"""

    boxes_for_tables = []
    cell_mask = np.zeros_like(original_cell_mask)

    cell_color = 1

    for table_box in table_boxes:

        # based on the table box, look whithin this box for the cell boxes
        table_mask = np.zeros_like(original_cell_mask)
        cv2.rectangle(table_mask, (table_box['xStart'], table_box['yStart']),
                      (table_box['xEnd'], table_box['yEnd']), (255, 255, 255), -1)

        gray_mask = cv2.cvtColor(original_cell_mask, cv2.COLOR_BGR2GRAY)
        # only observe the area in the table box, turn the rest to black
        gray_mask[table_mask[:, :, 0] == 0] = 0

        contours, hierarchy = cv2.findContours(gray_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]

        if image_to_overlay is not None:
            # generate an overlay to check that the annotations line up with the real table, this is for debugging
            overlay = np.zeros((cell_mask.shape[0], cell_mask.shape[1], 3)).astype(np.uint8)

        idx = 0
        boxes = []

        columns = []
        rows = []

        for cnt in reversed(contours):
            x, y, w, h = cv2.boundingRect(cnt)

            columns = check_and_add(columns, x)
            rows = check_and_add(rows, y)

            box_data = {'xStart': x, 'yStart': y, 'xEnd': x + w, 'yEnd': y + h, 'color': cell_color}
            boxes.append(box_data)
            cv2.drawContours(cell_mask, [cnt], -1, (cell_color, cell_color, cell_color), -1)

            if image_to_overlay is not None:
                # generate an overlay to check that the annotations line up with the real table, this is for debugging
                cv2.drawContours(overlay, contours, idx,
                                 (random.randrange(128, 256), random.randrange(128, 256), 0), -1)
            idx += 1
            cell_color += 1

        columns.sort()
        rows.sort()

        for box in boxes:
            box['column'] = get_index_of_sorted_list(columns, box['xStart'])
            box['row'] = get_index_of_sorted_list(rows, box['yStart'])

        table_box['boxes'] = boxes
        boxes_for_tables.append(table_box)

        if image_to_overlay is not None:
            # generate an overlay to check that the annotations line up with the real table, this is for debugging
            image_to_overlay[overlay > 0] = 0.5 * image_to_overlay[overlay > 0] + 0.5 * overlay[overlay > 0]
            image_to_overlay[:, :, 2][table_line_mask[:, :, 2] > 0] = 255
            image_to_overlay[:, :, 0:1][table_line_mask[:, :, 0:1] > 0] = 0

    return cell_mask, boxes_for_tables


def check_and_add(list, value):
    for element in list:
        if abs(element - value) < 12:
            return list

    list.append(value)

    return list


def get_index_of_sorted_list(presorted_list, value):
    for i in range(len(presorted_list)):
        if abs(presorted_list[i] - value) < 12:
            return i

    return -1
