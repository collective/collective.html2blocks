from bs4 import BeautifulSoup
from bs4 import Tag
from pathlib import Path
from slugify import slugify
from typing import Any

import pytest
import re
import yaml


@pytest.fixture(scope="session")
def test_resources_dir() -> Path:
    """
    Returns the absolute path to the test data directory (`_data`).
    Used for locating YAML and HTML files for test parametrization and fixtures.
    Session-scoped for efficiency.
    """
    return (Path(__file__).parent / "_data").resolve()


@pytest.fixture
def soup_from_str():
    """
    Returns a function that parses an HTML string into a BeautifulSoup object.
    Useful for quickly creating soup objects in tests.
    """

    def func(source: str) -> BeautifulSoup:
        soup = BeautifulSoup(source, features="html.parser")
        return soup

    return func


@pytest.fixture
def tag_from_str(soup_from_str):
    """
    Returns a function that parses an HTML string and returns the first Tag element.
    Useful for tests needing a single root tag from HTML input.
    Depends on soup_from_str fixture.
    """

    def func(source: str) -> Tag:
        soup = soup_from_str(source)
        return next(iter(soup.children))

    return func


def load_yaml_test_data():
    """
    Loads all YAML files from the test data directory (`_data`) and returns a dictionary
    mapping each filename (without extension) to its parsed YAML content.
    Used for parametrizing tests with external data.
    """
    data_path = (Path(__file__).parent / "_data").resolve()
    data = {}
    for filepath in data_path.glob("*.yml"):
        key = filepath.name[:-4]
        data[key] = yaml.safe_load(filepath.read_text())
    return data


TEST_DATA = load_yaml_test_data()


def pytest_generate_tests(metafunc):
    """
    Pytest hook for dynamic test parametrization using external YAML data.

    Logic:
    - The function name of the test is used as a key to look up test data in TEST_DATA.
    - If data is found, the test's 'setup' section defines argument names and which are constant vs. test-specific.
    - For each parameter entry, constant arguments are collected (with optional slugification for 'name').
    - For each test case in the entry, test-specific arguments are appended to the base.
    - All argument combinations are collected and passed to pytest's parametrize mechanism, enabling data-driven tests.

    This approach allows for flexible, maintainable, and readable test parametrization using external YAML files.
    """
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
    """
    Sets the working directory to a temporary path for the test.
    Returns the temporary directory Path object.
    Useful for tests that need isolated filesystem operations.
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def html_dir(test_resources_dir, test_dir):
    """
    Copies all HTML files from the test resources directory to the test directory.
    Returns the test directory Path object containing the copied HTML files.
    Useful for tests that need access to sample HTML files in an isolated environment.
    """
    for filepath in test_resources_dir.glob("*.html"):
        name = filepath.name
        src_data = filepath.read_text()
        dst = test_dir / name
        dst.write_text(src_data)
    return test_dir


@pytest.fixture(scope="session")
def traverse():
    """
    Returns a function to traverse nested dicts/lists using a path string.
    Supports optional function modifiers (e.g., 'len', 'type', 'is_uuid4', 'keys') via colon syntax.
    Example: traverse(data, 'foo/bar:baz')
    Session-scoped for reuse in multiple tests.
    """
    pattern = re.compile(r"'([^']+)'|([^/]+)")

    def func(data: dict | list, path: str) -> Any:
        func = None
        path_parts = path.split(":")
        if len(path_parts) == 2:
            func, path = path_parts
        else:
            path = path_parts[0]
        path_groups = pattern.findall(path)
        parts = [part[0] or part[1] for part in path_groups]
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
                value = type(value).__name__
            case "is_uuid4":
                value = len(value) == 32 and value[15] == "4"
            case "keys":
                value = list(value.keys()) if isinstance(value, dict) else []
        return value

    return func
