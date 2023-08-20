#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/1 11:19
@Author  : alexanderwu
@File    : test_config.py
@Modified By: mashenquan, 2013/8/20, Add `test_options`; remove global configuration `CONFIG`, enable configuration support for business isolation.
"""
from pathlib import Path

import pytest

from metagpt.config import Config


def test_config_class_get_key_exception():
    with pytest.raises(Exception) as exc_info:
        config = Config()
        config.get('wtf')
    assert str(exc_info.value) == "Key 'wtf' not found in environment variables or in the YAML file"


def test_config_yaml_file_not_exists():
    with pytest.raises(Exception) as exc_info:
        Config(Path('wtf.yaml'))
    assert str(exc_info.value) == "Set OPENAI_API_KEY or Anthropic_API_KEY first"


def test_options():
    filename = Path(__file__).resolve().parent.parent.parent.parent / "config/config.yaml"
    config = Config(filename)
    opts = config.runtime_options
    assert opts


if __name__ == '__main__':
    test_options()
