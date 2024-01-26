#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   :

from typing import Union
from xml.etree.ElementTree import Element, iterparse
import cv2
from pathlib import Path
import pyshine as ps
import re

from metagpt.config2 import config
from metagpt.logs import logger

from examples.andriod_assistant.utils.schema import AndroidElement
from examples.andriod_assistant.utils.schema import BaseOpParam, BaseGridOpParam, GridOp, ActionOp, TapOp, TapGridOp, \
    LongPressOp, LongPressGridOp, SwipeOp, SwipeGridOp, TextOp, ParamExtState


def get_id_from_element(elem: Element) -> str:
    bounds = elem.attrib["bounds"][1:-1].split("][")
    x1, y1 = map(int, bounds[0].split(","))
    x2, y2 = map(int, bounds[1].split(","))
    elem_w, elem_h = x2 - x1, y2 - y1
    if "resource-id" in elem.attrib and elem.attrib["resource-id"]:
        elem_id = elem.attrib["resource-id"].replace(":", ".").replace("/", "_")
    else:
        elem_id = f"{elem.attrib['class']}_{elem_w}_{elem_h}"
    if "content-desc" in elem.attrib and elem.attrib["content-desc"] and len(elem.attrib["content-desc"]) < 20:
        content_desc = elem.attrib["content-desc"].replace("/", "_").replace(" ", "").replace(":", "_")
        elem_id += f"_{content_desc}"
    return elem_id


def traverse_xml_tree(xml_path: Path, elem_list: list[AndroidElement], attrib: str, add_index=False):
    path = []
    for event, elem in iterparse(str(xml_path), ["start", "end"]):
        if event == "start":
            path.append(elem)
            if attrib in elem.attrib and elem.attrib[attrib] == "true":
                parent_prefix = ""
                if len(path) > 1:
                    parent_prefix = get_id_from_element(path[-2])
                bounds = elem.attrib["bounds"][1:-1].split("][")
                x1, y1 = map(int, bounds[0].split(","))
                x2, y2 = map(int, bounds[1].split(","))
                center = (x1 + x2) // 2, (y1 + y2) // 2
                elem_id = get_id_from_element(elem)
                if parent_prefix:
                    elem_id = parent_prefix + "_" + elem_id
                if add_index:
                    elem_id += f"_{elem.attrib['index']}"
                close = False
                for e in elem_list:
                    bbox = e.bbox
                    center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                    dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                    if dist <= config.get_other("min_dist"):
                        close = True
                        break
                if not close:
                    elem_list.append(AndroidElement(uid=elem_id, bbox=((x1, y1), (x2, y2)), attrib=attrib))

        if event == "end":
            path.pop()


def draw_bbox_multi(img_path: Path, output_path: Path, elem_list: list[AndroidElement], record_mode: bool = False,
                    dark_mode: bool = False):
    imgcv = cv2.imread(img_path)
    count = 1
    for elem in elem_list:
        try:
            top_left = elem.bbox[0]
            bottom_right = elem.bbox[1]
            left, top = top_left[0], top_left[1]
            right, bottom = bottom_right[0], bottom_right[1]
            label = str(count)
            if record_mode:
                if elem.attrib == "clickable":
                    color = (250, 0, 0)
                elif elem.attrib == "focusable":
                    color = (0, 0, 250)
                else:
                    color = (0, 250, 0)
                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10,
                                    text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=color,
                                    text_RGB=(255, 250, 250), alpha=0.5)
            else:
                text_color = (10, 10, 10) if dark_mode else (255, 250, 250)
                bg_color = (255, 250, 250) if dark_mode else (10, 10, 10)
                imgcv = ps.putBText(imgcv, label, text_offset_x=(left + right) // 2 + 10,
                                    text_offset_y=(top + bottom) // 2 + 10,
                                    vspace=10, hspace=10, font_scale=1, thickness=2, background_RGB=bg_color,
                                    text_RGB=text_color, alpha=0.5)
        except Exception as e:
            logger.error(f"ERROR: An exception occurs while labeling the image\n{e}")
        count += 1
    cv2.imwrite(output_path, imgcv)
    return imgcv


def draw_grid(img_path: Path, output_path: Path) -> tuple[int, int]:
    def get_unit_len(n):
        for i in range(1, n + 1):
            if n % i == 0 and 120 <= i <= 180:
                return i
        return -1

    image = cv2.imread(img_path)
    height, width, _ = image.shape
    color = (255, 116, 113)
    unit_height = get_unit_len(height)
    if unit_height < 0:
        unit_height = 120
    unit_width = get_unit_len(width)
    if unit_width < 0:
        unit_width = 120
    thick = int(unit_width // 50)
    rows = height // unit_height
    cols = width // unit_width
    for i in range(rows):
        for j in range(cols):
            label = i * cols + j + 1
            left = int(j * unit_width)
            top = int(i * unit_height)
            right = int((j + 1) * unit_width)
            bottom = int((i + 1) * unit_height)
            cv2.rectangle(image, (left, top), (right, bottom), color, thick // 2)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05) + 3, top + int(unit_height * 0.3) + 3), 0,
                        int(0.01 * unit_width), (0, 0, 0), thick)
            cv2.putText(image, str(label), (left + int(unit_width * 0.05), top + int(unit_height * 0.3)), 0,
                        int(0.01 * unit_width), color, thick)
    cv2.imwrite(output_path, image)
    return rows, cols


def area_to_xy(area: int, subarea: str, width: int, height: int, rows: int, cols: int) -> tuple[int, int]:
    area -= 1
    row, col = area // cols, area % cols
    x_0, y_0 = col * (width // cols), row * (height // rows)
    if subarea == "top-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 4
    elif subarea == "top":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 4
    elif subarea == "top-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 4
    elif subarea == "left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 2
    elif subarea == "right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 2
    elif subarea == "bottom-left":
        x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom":
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) * 3 // 4
    elif subarea == "bottom-right":
        x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) * 3 // 4
    else:
        x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 2
    return x, y


def elem_bbox_to_xy(bbox: tuple[tuple[int, int]]) -> tuple[int, int]:
    tl, br = bbox
    x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
    return x, y


def screenshot_parse_extract(parsed_json: dict, grid_on: bool = False) -> Union[BaseOpParam, BaseGridOpParam, GridOp]:
    act = parsed_json.get("Action")
    last_act = parsed_json.get("Summary")
    act_name = act.split("(")[0]

    if ParamExtState.FINISH.value.upper() in act:
        return BaseOpParam(param_state=ParamExtState.FINISH)

    if grid_on:
        return screenshot_parse_extract_with_grid(act_name, act, last_act)
    else:
        return screenshot_parse_extract_without_grid(act_name, act, last_act)


def op_params_clean(params: list[str]) -> list[Union[int, str]]:
    param_values = []
    for param_value in params:
        if '"' in param_value or "'" in param_value:  # remove `"`
            param_values.append(param_value.strip()[1:-1])
        else:
            param_values.append(int(param_value))
    return param_values


def screenshot_parse_extract_without_grid(act_name: str, act: str, last_act: str) -> Union[BaseOpParam, GridOp]:
    if act_name == ActionOp.TAP.value:
        area = int(re.findall(r"tap\((.*?)\)", act)[0])
        op = TapOp(act_name=act_name, area=area, last_act=last_act)
    elif act_name == ActionOp.TEXT.value:
        input_str = re.findall(r"text\((.*?)\)", act)[0][1:-1]
        op = TextOp(act_name=act_name, input_str=input_str, last_act=last_act)
    elif act_name == ActionOp.LONG_PRESS.value:
        area = int(re.findall(r"long_press\((.*?)\)", act)[0])
        op = LongPressOp(act_name=act_name, area=area, last_act=last_act)
    elif act_name == ActionOp.SWIPE.value:
        params = re.findall(r"swipe\((.*?)\)", act)[0].split(",")
        params = op_params_clean(params)  # area, swipe_orient, dist
        op = SwipeOp(act_name=act_name, area=params[0], swipe_orient=params[1], dist=params[2], last_act=last_act)
    elif act_name == ActionOp.GRID.value:
        op = GridOp(act_name=act_name)
    else:
        op = BaseOpParam(param_state=ParamExtState.FAIL)
    return op


def screenshot_parse_extract_with_grid(act_name: str, act: str, last_act: str) -> Union[BaseGridOpParam, GridOp]:
    if act_name == ActionOp.TAP.value:
        params = re.findall(r"tap\((.*?)\)", act)[0].split(",")
        params = op_params_clean(params)
        op = TapGridOp(act_name=act_name, area=params[0], subarea=params[1], last_act=last_act)
    elif act_name == ActionOp.LONG_PRESS.value:
        params = re.findall(r"long_press\((.*?)\)", act)[0].split(",")
        params = op_params_clean(params)
        op = LongPressGridOp(act_name=act_name, area=params[0], subarea=params[1], last_act=last_act)
    elif act_name == ActionOp.SWIPE.value:
        params = re.findall(r"swipe\((.*?)\)", act)[0].split(",")
        params = op_params_clean(params)
        op = SwipeGridOp(act_name=act_name,
                         start_area=params[0],
                         start_subarea=params[1],
                         end_area=params[2],
                         end_subarea=params[3])
    elif act_name == ActionOp.GRID.value:
        op = GridOp(act_name=act_name)
    else:
        op = BaseGridOpParam(param_state=ParamExtState.FAIL)
    return op
