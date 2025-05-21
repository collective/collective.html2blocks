from bs4 import BeautifulSoup
from bs4 import Tag
from pathlib import Path
from slugify import slugify
from typing import Any

import pytest
import yaml


@pytest.fixture(scope="session")
def test_resources_dir() -> Path:
    return (Path(__file__).parent / "_data").resolve()


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
                # This makes it easier to compare
                value = type(value).__name__
            case "is_uuid4":
                value = len(value) == 32 and value[15] == "4"
            case "keys":
                value = list(value.keys())
            case "keys":
                value = list(value.keys())
        return value

    return func


def load_yaml_test_data():
    data_path = (Path(__file__).parent / "_data").resolve()
    data = {}
    for filepath in data_path.glob("*.yml"):
        key = filepath.name[:-4]
        data[key] = yaml.safe_load(filepath.read_text())
    return data


TEST_DATA = load_yaml_test_data()


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    if func_name in TEST_DATA:
        data = TEST_DATA[func_name]
        setup = data["setup"]
        argnames = setup["argnames"]
        test_args = setup["test_args"]
        const_args = [name for name in argnames if name not in test_args]
        args = []
        for entry in data["params"]:
            base = []
            for name in const_args:
                value = entry[name]
                if name == "name":
                    # Slugify
                    value = f"{value} ({slugify(value)})"
                base.append(value)
            for test in entry["tests"]:
                item = base + [test[name] for name in test_args]
                args.append(item)
        metafunc.parametrize(argnames, args)


@pytest.fixture
def test_dir(monkeypatch, tmp_path) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def html_dir(test_resources_dir, test_dir):
    for filepath in test_resources_dir.glob("*.html"):
        name = filepath.name
        src_data = filepath.read_text()
        dst = test_dir / name
        dst.write_text(src_data)
    return test_dir
