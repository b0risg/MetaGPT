#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : LIKE scripts/task_executor.py in stage=act

import ast
from pathlib import Path

from examples.andriod_assistant.actions.screenshot_parse_an import SCREENSHOT_PARSE_NODE
from examples.andriod_assistant.prompts.assistant_prompt import (
    screenshot_parse_template,
    screenshot_parse_with_grid_template,
)
from examples.andriod_assistant.utils.schema import (
    AndroidActionOutput,
    AndroidElement,
    GridOp,
    LongPressGridOp,
    LongPressOp,
    OpLogItem,
    RunState,
    SwipeGridOp,
    SwipeOp_3,
    TapGridOp,
    TapOp,
    TextOp,
)
from examples.andriod_assistant.utils.utils import (
    area_to_xy,
    draw_bbox_multi,
    draw_grid,
    elem_bbox_to_xy,
    screenshot_parse_extract,
    traverse_xml_tree,
)
from metagpt.actions.action import Action
from metagpt.config2 import config
from metagpt.const import ADB_EXEC_FAIL
from metagpt.environment.android_env.android_env import AndroidEnv
from metagpt.environment.api.env_api import EnvAPIAbstract
from metagpt.utils.common import encode_image


class ScreenshotParse(Action):
    name: str = "ScreenshotParse"

    def _makeup_ui_document(self, elem_list: list[AndroidElement], docs_idr: Path, use_exist_doc: bool = True) -> str:
        if not use_exist_doc:
            return ""

        ui_doc = """
        You also have access to the following documentations that describes the functionalities of UI 
        elements you can interact on the screen. These docs are crucial for you to determine the target of your 
        next action. You should always prioritize these documented elements for interaction:"""
        for i, elem in enumerate(elem_list):
            doc_path = docs_idr.joinpath(f"{elem.uid}.txt")
            if not doc_path.exists():
                continue
            ui_doc += f"Documentation of UI element labeled with the numeric tag '{i + 1}':\n"
            doc_content = ast.literal_eval(open(doc_path, "r").read())
            if doc_content["tap"]:
                ui_doc += f"This UI element is clickable. {doc_content['tap']}\n\n"
            if doc_content["text"]:
                ui_doc += (
                    f"This UI element can receive text input. The text input is used for the following "
                    f"purposes: {doc_content['text']}\n\n"
                )
            if doc_content["long_press"]:
                ui_doc += f"This UI element is long clickable. {doc_content['long_press']}\n\n"
            if doc_content["v_swipe"]:
                ui_doc += (
                    f"This element can be swiped directly without tapping. You can swipe vertically on "
                    f"this UI element. {doc_content['v_swipe']}\n\n"
                )
            if doc_content["h_swipe"]:
                ui_doc += (
                    f"This element can be swiped directly without tapping. You can swipe horizontally on "
                    f"this UI element. {doc_content['h_swipe']}\n\n"
                )
        return ui_doc

    async def run(
        self,
        round_count: int,
        task_desc: str,
        last_act: str,
        task_dir: Path,
        docs_dir: Path,
        grid_on: bool,
        env: AndroidEnv,
    ):
        for path in [task_dir, docs_dir]:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

        screenshot_path: Path = await env.observe(
            EnvAPIAbstract(
                api_name="get_screenshot", kwargs={"ss_name": f"{round_count}_before", "local_save_dir": task_dir}
            )
        )
        xml_path: Path = await env.observe(
            EnvAPIAbstract(api_name="get_xml", kwargs={"xml_name": f"{round_count}", "local_save_dir": task_dir})
        )
        width, height = env.device_shape
        if not screenshot_path.exists() or not xml_path.exists():
            return AndroidActionOutput(action_state=RunState.FAIL)

        clickable_list = []
        focusable_list = []
        traverse_xml_tree(xml_path, clickable_list, "clickable", True)
        traverse_xml_tree(xml_path, focusable_list, "focusable", True)
        elem_list: list[AndroidElement] = clickable_list.copy()
        for elem in focusable_list:
            bbox = elem.bbox
            center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
            close = False
            for e in clickable_list:
                bbox = e.bbox
                center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                if dist <= config.get_other("min_dist"):
                    close = True
                    break
            if not close:
                elem_list.append(elem)

        screenshot_labeled_path = task_dir.joinpath(f"{round_count}_labeled.png")
        draw_bbox_multi(screenshot_path, screenshot_labeled_path, elem_list)
        img_base64 = encode_image(screenshot_labeled_path)

        parse_template = screenshot_parse_with_grid_template if grid_on else screenshot_parse_template

        if grid_on:
            env.rows, env.cols = draw_grid(screenshot_path, task_dir / f"{round_count}_grid.png")

        ui_doc = self._makeup_ui_document(elem_list, docs_dir)
        context = parse_template.format(ui_document=ui_doc, task_description=task_desc, last_act=last_act)
        node = await SCREENSHOT_PARSE_NODE.fill(context=context, llm=self.llm, images=[img_base64])

        if "error" in node.content:
            return AndroidActionOutput(action_state=RunState.FAIL)

        prompt = node.compile(context=context, schema="json", mode="auto")
        OpLogItem(step=round_count, prompt=prompt, image=str(screenshot_labeled_path), response=node.content)

        op_param = screenshot_parse_extract(node.instruct_content.model_dump(), grid_on)
        if op_param.param_state == RunState.FINISH:
            return AndroidActionOutput(action_state=RunState.FINISH)
        if op_param.param_state == RunState.FAIL:
            return AndroidActionOutput(action_state=RunState.FAIL)

        if isinstance(op_param, TapOp):
            x, y = elem_bbox_to_xy(elem_list[op_param.area - 1].bbox)
            res = await env.step(EnvAPIAbstract(api_name="system_tap", kwargs={"x": x, "y": y}))
            if res == ADB_EXEC_FAIL:
                return AndroidActionOutput(action_state=RunState.FAIL)
        elif isinstance(op_param, TextOp):
            res = await env.step(EnvAPIAbstract(api_name="user_input", kwargs={"input_txt": op_param.input_str}))
            if res == ADB_EXEC_FAIL:
                return AndroidActionOutput(action_state=RunState.FAIL)
        elif isinstance(op_param, LongPressOp):
            x, y = elem_bbox_to_xy(elem_list[op_param.area - 1].bbox)
            res = await env.step(EnvAPIAbstract(api_name="user_longpress", kwargs={"x": x, "y": y}))
            if res == ADB_EXEC_FAIL:
                return AndroidActionOutput(action_state=RunState.FAIL)
        elif isinstance(op_param, SwipeOp_3):
            x, y = elem_bbox_to_xy(elem_list[op_param.area - 1].bbox)
            res = await env.step(
                EnvAPIAbstract(
                    api_name="user_swipe",
                    kwargs={"x": x, "y": y, "orient": op_param.swipe_orient, "dist": op_param.dist},
                )
            )
            if res == ADB_EXEC_FAIL:
                return AndroidActionOutput(action_state=RunState.FAIL)
        elif isinstance(op_param, GridOp):
            grid_on = True
        elif isinstance(op_param, TapGridOp) or isinstance(op_param, LongPressGridOp):
            x, y = area_to_xy(op_param.area, op_param.subarea, env.width, env.height, env.rows, env.cols)
            if isinstance(op_param, TapGridOp):
                res = await env.step(EnvAPIAbstract(api_name="system_tap", kwargs={"x": x, "y": y}))
                if res == ADB_EXEC_FAIL:
                    return AndroidActionOutput(action_state=RunState.FAIL)
            else:
                # LongPressGridOp
                res = await env.step(EnvAPIAbstract(api_name="user_longpress", kwargs={"x": x, "y": y}))
                if res == ADB_EXEC_FAIL:
                    return AndroidActionOutput(action_state=RunState.FAIL)
        elif isinstance(op_param, SwipeGridOp):
            start_x, start_y = area_to_xy(
                op_param.start_area, op_param.start_subarea, env.width, env.height, env.rows, env.cols
            )
            end_x, end_y = area_to_xy(
                op_param.end_area, op_param.end_subarea, env.width, env.height, env.rows, env.cols
            )
            res = await env.step(
                EnvAPIAbstract(api_name="user_swipe_to", kwargs={"start": (start_x, start_y), "end": (end_x, end_y)})
            )
            if res == ADB_EXEC_FAIL:
                return AndroidActionOutput(action_state=RunState.FAIL)

        if op_param.act_name != "grid":
            grid_on = True

        return AndroidActionOutput(data={"grid_on": grid_on})
