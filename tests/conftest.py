from bs4 import BeautifulSoup
from bs4 import Tag
from typing import Any

import pytest


@pytest.fixture
def soup_from_str():
    def func(source: str) -> BeautifulSoup:
        soup = BeautifulSoup(source, features="html.parser")
        return soup

    return func


@pytest.fixture
def tag_from_str(soup_from_str):
    def func(source: str) -> Tag:
        soup = soup_from_str(source)
        return next(iter(soup.children))

    return func


@pytest.fixture
def traverse():
    def func(data: dict | list, path: str) -> Any:
        func = None
        path = path.split(":")
        if len(path) == 2:
            func, path = path
        else:
            path = path[0]
        parts = [part for part in path.split("/") if part.strip()]
        value = data
        for part in parts:
            if isinstance(value, list):
                part = int(part)
            value = value[part]
        match func:
            # Add other functions here
            case "len":
                value = len(value)
            case "type":
                value = type(value)
        return value

    return func
