"""[TODO:description]

[TODO:description]
"""

from langchain.tools import tool


@tool
def search_file_path(file_path: str):
    """Use to search file path"""
    return "path/to/Projects/harness_agent"


@tool
def bash_file(content: str):
    """Use to bash file"""
    return "This is testing tool"


@tool
def search_letter():
    pass


@tool
def edit_file():
    pass


@tool
def delete_file():
    pass
