import ast
import contextlib
from typing import Literal

from metagpt.actions.action import Action
from metagpt.utils.common import OutputParser
from metagpt.utils.pycst import merge_docstring

PYTHON_DOCSTRING_SYSTEM = '''### Requirements
1. Add docstrings to the given code following the {style} style.
2. Remove all private members whose names start with an underscore, such as `_test` and `__init__`.
3. Replace the function body with an Ellipsis object(...) to reduce output.
4. If the types are already annotated, there is no need to include them in the docstring.
5. Only output Python code and avoid including any other text.

### Input Example
```python
def function_with_pep484_type_annotations(param1: int) -> bool:
    return isinstanc(param1, int)

class ExampleError(Exception):
    def __init__(self, msg: str):
        self.msg = msg
```

### Output Example
```python{example}```
'''

# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

PYTHON_DOCSTRING_EXAMPLE_GOOGLE = '''
def function_with_pep484_type_annotations(param1: int) -> bool:
    """Example function with PEP 484 type annotations.

    Extended description of function.

    Args:
        param1: The first parameter.

    Returns:
        The return value. True for success, False otherwise.
    """
    ...

class ExampleError(Exception):
    """Exceptions are documented in the same way as classes.

    The __init__ method was documented in the class level docstring.

    Args:
        msg: Human readable string describing the exception.

    Attributes:
        msg: Human readable string describing the exception.
    """
    ...
'''

PYTHON_DOCSTRING_EXAMPLE_NUMPY = '''
def function_with_pep484_type_annotations(param1: int) -> bool:
    """
    Example function with PEP 484 type annotations.

    Extended description of function.

    Parameters
    ----------
    param1
        The first parameter.

    Returns
    -------
    bool
        The return value. True for success, False otherwise.
    """
    ...

class ExampleError(Exception):
    """
    Exceptions are documented in the same way as classes.

    The __init__ method was documented in the class level docstring.

    Parameters
    ----------
    msg
        Human readable string describing the exception.

    Attributes
    ----------
    msg
        Human readable string describing the exception.
    """
    ...
'''

PYTHON_DOCSTRING_EXAMPLE_SPHINX = '''
def function_with_pep484_type_annotations(param1: int) -> bool:
    """Example function with PEP 484 type annotations.

    Extended description of function.

    :param param1: The first parameter.
    :type param1: int

    :return: The return value. True for success, False otherwise.
    :rtype: bool
    """
    ...

class ExampleError(Exception):
    """Exceptions are documented in the same way as classes.

    The __init__ method was documented in the class level docstring.

    :param msg: Human-readable string describing the exception.
    :type msg: str
    """
    ...
'''

_python_docstring_style = {
    "google": PYTHON_DOCSTRING_EXAMPLE_GOOGLE,
    "numpy": PYTHON_DOCSTRING_EXAMPLE_NUMPY,
    "sphinx": PYTHON_DOCSTRING_EXAMPLE_SPHINX,
}


class WriteDocstring(Action):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.desc = "Write docstring for code."

    async def run(
        self, code: str,
        system_text: str = PYTHON_DOCSTRING_SYSTEM,
        style: Literal["google", "numpy", "sphinx"] = "google",
    ) -> str:
        system_text = system_text.format(style=style, example=_python_docstring_style[style])
        simplified_code = _simplify_python_code(code)
        documented_code = await self._aask(simplified_code, [system_text])
        with contextlib.suppress(Exception):
            documented_code = OutputParser.parse_code(documented_code)
        return merge_docstring(code, documented_code)


def _simplify_python_code(code: str) -> None:
    code_tree = ast.parse(code)
    code_tree.body = [i for i in code_tree.body if not isinstance(i, ast.Expr)]
    if isinstance(code_tree.body[-1], ast.If):
        code_tree.body.pop()
    return ast.unparse(code_tree)


if __name__ == "__main__":
    import fire

    async def run(filename: str, overwrite: bool = False, style: Literal["google", "numpy", "sphinx"] = "google"):
        with open(filename) as f:
            code = f.read()
        code = await WriteDocstring().run(code, style=style)
        if overwrite:
            with open(filename, "w") as f:
                f.write(code)
        return code

    fire.Fire(run)
