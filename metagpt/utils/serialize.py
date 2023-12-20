#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : the implement of serialization and deserialization

import copy
import pickle

from metagpt.utils.common import import_class


def actionoutout_schema_to_mapping(schema: dict) -> dict:
    """
    directly traverse the `properties` in the first level.
    schema structure likes
    ```
    {
        "title":"prd",
        "type":"object",
        "properties":{
            "Original Requirements":{
                "title":"Original Requirements",
                "type":"string"
            },
        },
        "required":[
            "Original Requirements",
        ]
    }
    ```
    """
    mapping = dict()
    for field, property in schema["properties"].items():
        if property["type"] == "string":
            mapping[field] = (str, ...)
        elif property["type"] == "array" and property["items"]["type"] == "string":
            mapping[field] = (list[str], ...)
        elif property["type"] == "array" and property["items"]["type"] == "array":
            # here only consider the `list[list[str]]` situation
            mapping[field] = (list[list[str]], ...)
    return mapping


def actionoutput_mapping_to_str(mapping: dict) -> dict:
    new_mapping = {}
    for key, value in mapping.items():
        new_mapping[key] = str(value)
    return new_mapping


def actionoutput_str_to_mapping(mapping: dict) -> dict:
    new_mapping = {}
    for key, value in mapping.items():
        if value == "(<class 'str'>, Ellipsis)":
            new_mapping[key] = (str, ...)
        else:
            new_mapping[key] = eval(value)  # `"'(list[str], Ellipsis)"` to `(list[str], ...)`
    return new_mapping


def serialize_general_message(message: "Message") -> dict:
    """ serialize Message, not to save"""
    message_cp = copy.deepcopy(message)
    ic = message_cp.instruct_content
    if ic:
        # model create by pydantic create_model like `pydantic.main.prd`, can't pickle.dump directly
        schema = ic.schema()
        mapping = actionoutout_schema_to_mapping(schema)
        mapping = actionoutput_mapping_to_str(mapping)

        message_cp.instruct_content = {"class": schema["title"], "mapping": mapping, "value": ic.dict()}
    return message_cp.dict()


def serialize_message(message: "Message"):
    message_cp = copy.deepcopy(message)  # avoid `instruct_content` value update by reference
    ic = message_cp.instruct_content
    if ic:
        # model create by pydantic create_model like `pydantic.main.prd`, can't pickle.dump directly
        schema = ic.schema()
        mapping = actionoutout_schema_to_mapping(schema)

        message_cp.instruct_content = {"class": schema["title"], "mapping": mapping, "value": ic.dict()}
    msg_ser = pickle.dumps(message_cp)

    return msg_ser


def deserialize_general_message(message_dict: dict) -> "Message":
    """ deserialize Message, not to load"""
    instruct_content = message_dict.pop("instruct_content")
    cause_by = message_dict.pop("cause_by")

    message_cls = import_class("Message", "metagpt.schema")
    message = message_cls(**message_dict)
    if instruct_content:
        ic = instruct_content
        mapping = actionoutput_str_to_mapping(ic["mapping"])

        actionoutput_class = import_class("ActionOutput", "metagpt.actions.action_output")
        ic_obj = actionoutput_class.create_model_class(class_name=ic["class"], mapping=mapping)
        ic_new = ic_obj(**ic["value"])
        message.instruct_content = ic_new

    return message


def deserialize_message(message_ser: str) -> "Message":
    message = pickle.loads(message_ser)
    if message.instruct_content:
        ic = message.instruct_content

        actionoutput_class = import_class("ActionOutput", "metagpt.actions.action_output")
        ic_obj = actionoutput_class.create_model_class(class_name=ic["class"], mapping=ic["mapping"])
        ic_new = ic_obj(**ic["value"])
        message.instruct_content = ic_new

    return message
