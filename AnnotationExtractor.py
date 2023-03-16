import cv2
import numpy as np
import imutils
import random
import matplotlib.pyplot as plt
import json
import math


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


def get_signature_annotations(image_boxes, list_signatures, overlay_image=None):
    image_boxes_grey = cv2.cvtColor(image_boxes, cv2.COLOR_BGR2GRAY)
    boxes = []

    color_thresh = cv2.threshold(image_boxes_grey, 1, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(color_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    thickness = 1
    for cntr in contours:

        M = cv2.moments(cntr)
        if M["m00"] != 0:

            # calc center of contour
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # determine its color in rgb
            color = list(np.array(image_boxes[cY, cX]))
            color.reverse()

            # all signatures with this color
            all_candidates = list(filter(lambda item: item["color"] == color, list_signatures))

            if len(all_candidates) == 1:

                current_image = all_candidates[0]
                transform = current_image['transform']
                [w_image, h_image] = current_image['shape']
                bot_left, top_right = calc_bb_rotated_rectangle([cX, cY], transform, [h_image, w_image])

                if overlay_image is not None:
                    overlay_image = cv2.rectangle(overlay_image, bot_left, top_right, (0, 255, 0), thickness)

                box_data = {'xStart': bot_left[0], 'yStart': bot_left[1], 'xEnd': top_right[0], 'yEnd': top_right[1]}
                boxes.append(box_data)

            else:
                print(f"Warning: Did not find one matching signature, instead found {len(all_candidates)}")
        else:
            print(f"Warning: Contour has zero area")

    return boxes


def get_handwritten_annotations(image_boxes, list_handwriting, overlay_image=None):
    image_boxes_grey = cv2.cvtColor(image_boxes, cv2.COLOR_BGR2GRAY)
    boxes = []

    color_thresh = cv2.threshold(image_boxes_grey, 1, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(color_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    thickness = 1

    for cntr in contours:
        M = cv2.moments(cntr)
        if M["m00"] != 0:
            # calc center of contour
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # determine its color in rgb
            color = list(np.array(image_boxes[cY, cX]))
            color.reverse()

            # all signatures with this color
            all_candidates = list(filter(lambda item: color in item["color"], list_handwriting))

            if len(all_candidates) == 1:
                handwriting_group = all_candidates[0]
                list_handwriting.remove(handwriting_group)
                new_color_box = {'contour': cntr, 'color': color, 'center': [cX, cY]}
                if 'color_box' in handwriting_group:
                    handwriting_group['color_box'].append(new_color_box)
                else:
                    handwriting_group['color_box'] = [new_color_box]
                list_handwriting.append(handwriting_group)

            else:
                print(f"Warning: Did not find one matching handwriting, instead found {len(all_candidates)}")
    else:
        print(f"Warning: Contour has zero area")

    # for each handwriting_group one bounding_box
    for handwriting_group in list_handwriting:
        if 'color_box' in handwriting_group:
            bb_edges_x = []
            bb_edges_y = []
            for color_box in handwriting_group['color_box']:
                index = handwriting_group['color'].index(color_box['color'])
                [inner_w, inner_h] = handwriting_group['shape'][index]
                bot_left, top_right = calc_bb_rotated_rectangle(color_box['center'],
                                                                handwriting_group['transform'], [inner_h, inner_w])

                if overlay_image is not None:
                    overlay_image = cv2.rectangle(overlay_image, bot_left, top_right, (255, 255, 0),
                                                  thickness)
                bb_edges_x.extend([bot_left[0], top_right[0]])
                bb_edges_y.extend([bot_left[1], top_right[1]])

            total_bot_left, total_top_right = calc_bb_handwriting_group(bb_edges_x, bb_edges_y)

            box_data = {'xStart': total_bot_left[0], 'yStart': total_bot_left[1],
                        'xEnd': total_top_right[0], 'yEnd': total_top_right[1]}
            boxes.append(box_data)
            if overlay_image is not None:
                overlay_image = cv2.rectangle(overlay_image, total_bot_left, total_top_right, (0, 255, 0), thickness)
        else:
            print(f"Warning: handwriting group {handwriting_group['text']} has no matching color_box")

    return boxes


def calc_bb_handwriting_group(bb_edges_x, bb_edges_y):
    min_x, max_x = min(bb_edges_x), max(bb_edges_x)
    min_y, max_y = min(bb_edges_y), max(bb_edges_y)

    return (int(min_x), int(min_y)), (math.ceil(max_x), math.ceil(max_y))


def calc_bb_rotated_rectangle(center, transform, size):
    angle = (transform['rotation'] / 360) * 2 * math.pi
    height = size[0] * transform['scale']
    width = size[1] * transform['scale']
    center_x = center[0]
    center_y = center[1]

    # top_right
    top_right_x = center_x + ((width / 2) * math.cos(angle)) - ((height / 2) * math.sin(angle))
    top_right_y = center_y + ((width / 2) * math.sin(angle)) + ((height / 2) * math.cos(angle))

    # top_left
    top_left_x = center_x - ((width / 2) * math.cos(angle)) - ((height / 2) * math.sin(angle))
    top_left_y = center_y - ((width / 2) * math.sin(angle)) + ((height / 2) * math.cos(angle))

    # bottom_left:
    bot_left_x = center_x - ((width / 2) * math.cos(angle)) + ((height / 2) * math.sin(angle))
    bot_left_y = center_y - ((width / 2) * math.sin(angle)) - ((height / 2) * math.cos(angle))

    # bottom_right:
    bot_right_x = center_x + ((width / 2) * math.cos(angle)) + ((height / 2) * math.sin(angle))
    bot_right_y = center_y + ((width / 2) * math.sin(angle)) - ((height / 2) * math.cos(angle))

    # calc min and max for surrounding rectangle
    x_values = [top_right_x, top_left_x, bot_left_x, bot_right_x]
    y_values = [top_right_y, top_left_y, bot_left_y, bot_right_y]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)

    return (int(min_x), int(min_y)), (math.ceil(max_x), math.ceil(max_y))


def get_print_annotations(image_boxes, image_to_overlay=None):
    grey_image_boxes = cv2.cvtColor(image_boxes, cv2.COLOR_BGR2GRAY)
    contours, hierarchy = cv2.findContours(grey_image_boxes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]

    boxes = []

    for cnt in reversed(contours):
        x, y, w, h = cv2.boundingRect(cnt)

        box_data = {'xStart': x, 'yStart': y, 'xEnd': x + w, 'yEnd': y + h}

        boxes.append(box_data)

        if image_to_overlay is not None:
            # generate an overlay to check that the annotations line up with the real table, this is for debugging
            cv2.rectangle(image_to_overlay, (x, y), (x + w, y + h), (255, 0, 0), 1)

    return boxes


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



        if image_to_overlay is not None:
            # generate an overlay to check that the annotations line up with the real table, this is for debugging
            image_to_overlay[overlay > 0] = 0.5 * image_to_overlay[overlay > 0] + 0.5 * overlay[overlay > 0]
            image_to_overlay[:, :, 2][table_line_mask[:, :, 2] > 0] = 255
            image_to_overlay[:, :, 0:1][table_line_mask[:, :, 0:1] > 0] = 0

        table_box['boxes'] = boxes
        horizontal_lines, vertical_lines = get_line_annotations(table_box, boxes, columns, rows)
        boxes_for_tables.append(table_box)

        table_box['horizontal_lines'] , table_box['vertical_lines']\
            = get_line_annotations(table_box, boxes, columns, rows)

    return cell_mask, boxes_for_tables


def get_line_annotations(tablebox, boxes, columns, rows):
    # max and min values for inner-line-coordinates
    y_min, y_max = 0, 0
    x_min, x_max = 0, 0

    # get vertical lines separating two cells
    vertical_short_lines = []
    for row in range(len(rows)):
        current_row = [box for box in boxes if box['row'] == row]
        for col in range(len(columns) - 1):
            left_box = next((box for box in current_row if box['column'] == col), None)
            right_box = next((box for box in current_row if box['column'] == col + 1), None)
            line = get_vertical_separating_line(left_box, right_box)
            line['row'] = row
            line['column'] = col
            vertical_short_lines.append(line)

    # merge vertical lines to one large line
    vertical_lines = []
    for col in range(len(columns) - 1):
        column_lines = [line for line in vertical_short_lines if line['column'] == col]
        start_line = next((line for line in column_lines if line['row'] == 0), None)
        end_line = next((line for line in column_lines if line['row'] == len(rows) - 1), None)
        merged_line = {'startPoint': start_line['startPoint'], 'endPoint': end_line['endPoint']}
        vertical_lines.append(merged_line)
        y_min, y_max = start_line['startPoint'][1], end_line['endPoint'][1]

    # get horizontal lines separating two cells
    horizontal_short_lines = []
    for col in range(len(columns)):
        current_column = [box for box in boxes if box['column'] == col]
        for row in range(len(rows) - 1):
            top_box = next((box for box in current_column if box['row'] == row), None)
            bottom_box = next((box for box in current_column if box['row'] == row + 1), None)
            line = get_horizontal_separating_line(top_box, bottom_box)
            line['row'] = row
            line['column'] = col
            horizontal_short_lines.append(line)

    # merge horizontal lines to one large line
    horizontal_lines = []
    for row in range(len(rows) - 1):
        row_lines = [line for line in horizontal_short_lines if line['row'] == row]
        start_line = next((line for line in row_lines if line['column'] == 0), None)
        end_line = next((line for line in row_lines if line['column'] == len(columns) - 1), None)
        merged_line = {'startPoint': start_line['startPoint'], 'endPoint': end_line['endPoint']}
        horizontal_lines.append(merged_line)
        x_min, x_max = start_line['startPoint'][0], end_line['endPoint'][0]

    top_line, bottom_line, left_line, right_line = get_surrounding_lines_of_table(tablebox, y_min, y_max, x_min, x_max)

    horizontal_lines.append(top_line)
    horizontal_lines.append(bottom_line)

    vertical_lines.append(right_line)
    vertical_lines.append(left_line)

    return horizontal_lines, vertical_lines


def get_surrounding_lines_of_table(tablebox, y_min, y_max, x_min, x_max):
    # get surrounding boxes of table
    x_start = calc_middle(tablebox['xStart'], x_min)
    x_end = calc_middle(x_max, tablebox['xEnd'])
    y_start = calc_middle(y_min, tablebox['yStart'])
    y_end = calc_middle(tablebox['yEnd'], y_max)
    top_line = {'startPoint': (x_start, y_start),
                'endPoint': (x_end, y_start)}
    bottom_line = {'startPoint': (x_start, y_end),
                   'endPoint': (x_end, y_end)}

    left_line = {'startPoint': (x_start, y_start),
                 'endPoint': (x_start, y_end)}
    right_line = {'startPoint': (x_end, y_start),
                  'endPoint': (x_end, y_end)}

    return top_line, bottom_line, left_line, right_line


def calc_middle(higher_value, lower_value):
    return int((higher_value - lower_value) / 2 + lower_value)


def get_horizontal_separating_line(top_box, bottom_box):
    x_start = min(top_box['xStart'], bottom_box['xStart'])
    y_start = int(top_box['yEnd'] + ((bottom_box['yStart'] - top_box['yEnd']) / 2))

    x_end = max(top_box['xEnd'], bottom_box['xEnd'])
    y_end = int(top_box['yEnd'] + ((bottom_box['yStart'] - top_box['yEnd']) / 2))
    return {'startPoint': (x_start, y_start), 'endPoint': (x_end, y_end)}


def get_vertical_separating_line(left_box, right_box):
    y_start = min(left_box['yStart'], right_box['yStart'])
    x_start = int(left_box['xEnd'] + ((right_box['xStart'] - left_box['xEnd']) / 2))

    y_end = max(left_box['yEnd'], right_box['yEnd'])
    x_end = int(left_box['xEnd'] + ((right_box['xStart'] - left_box['xEnd']) / 2))
    return {'startPoint': (x_start, y_start), 'endPoint': (x_end, y_end)}


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
