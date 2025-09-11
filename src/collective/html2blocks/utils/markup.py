"""
HTML markup utilities for collective.html2blocks.

This module provides functions for parsing, normalizing, and extracting
information from HTML markup, including grouping inline elements, filtering,
normalizing, and extracting table and style information.

Example usage::

    from collective.html2blocks.utils import markup
    soup = markup.parse_source('<p>Hello <b>world</b></p>')
    children = markup.all_children(soup)
"""

from .inline import ALLOW_EMPTY_ELEMENTS
from .inline import INLINE_ELEMENTS
from bs4 import BeautifulSoup
from bs4.element import Comment
from bs4.element import NavigableString
from bs4.element import PageElement
from collections.abc import Iterable
from collective.html2blocks._types import Tag
from urllib import parse


def _group_inline_elements(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Group inline elements into paragraphs in the soup.

    Args:
        soup (BeautifulSoup): The soup to process.

    Returns:
        BeautifulSoup: The modified soup with inline elements grouped.
    """
    wrapper = None
    children = list(soup.children)
    for element in children:
        if inline_element := is_inline(element, True):
            if not wrapper:
                wrapper = soup.new_tag("p")
                element.insert_before(wrapper)
            wrapper.append(element.extract())
        elif not inline_element and wrapper:
            if wrapper.text == "\n":
                wrapper.extract()
            wrapper = None
    return soup


def _filter_children(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Filter out comments and empty elements from the soup.

    Args:
        soup (BeautifulSoup): The soup to process.

    Returns:
        BeautifulSoup: The filtered soup.
    """
    children = list(soup.children)
    for child in children:
        if isinstance(child, Comment) or (
            isinstance(child, NavigableString) and child.text == "\n"
        ):
            child.extract()
    children = list(soup.children)
    if (
        len(children) == 1
        and isinstance(children[0], Tag)
        and children[0].name == "div"
    ):
        # If there is only a wraping div, return its children
        new_soup = BeautifulSoup("", features="html.parser")
        internal_ = list(children[0].children)
        for child in internal_:
            child = child.extract()
            new_soup.append(child)
        soup = _filter_children(new_soup)
    return soup


def _normalize_html(soup: BeautifulSoup, block_level_tags: Iterable[str] = ()):
    """
    Normalize HTML by simplifying, removing empty tags, and wrapping paragraphs.

    Args:
        soup (BeautifulSoup): The soup to normalize.
        block_level_tags (Iterable[str], optional): Block-level tags to wrap.
                                                    Defaults to ().

    Returns:
        BeautifulSoup: The normalized soup.
    """
    _recursively_simplify(soup)
    _remove_empty_tags(soup)
    _wrap_all_paragraphs(soup, block_level_tags)
    return soup


def _recursively_simplify(tag: Tag):
    """
    Recursively simplify nested tags with identical names and attributes.

    Args:
        tag (Tag): The tag to simplify.
    """
    for child in list(tag.children):
        if isinstance(child, Tag):
            _recursively_simplify(child)

    if len(tag.contents) == 1 and isinstance(tag.contents[0], Tag):
        child = tag.contents[0]
        if tag.name == child.name and tag.attrs == child.attrs:
            tag.replace_with(child)
            _recursively_simplify(child)


def is_empty(tag: Tag | NavigableString) -> bool:
    """
    Check if a tag or string is empty (not allowed or has no content).

    Args:
        tag (Tag | NavigableString): The tag or string to check.

    Returns:
        bool: True if empty, False otherwise.
    """
    if isinstance(tag, NavigableString):
        return tag.strip() == ""
    return (
        tag.name not in ALLOW_EMPTY_ELEMENTS
        and not tag.contents
        and not tag.string
        and not tag.attrs
    )


def is_ignorable(el: PageElement) -> bool:
    """
    Check if an element is ignorable (empty string or allowed empty tag).

    Args:
        el (PageElement): The element to check.

    Returns:
        bool: True if ignorable, False otherwise.
    """
    return (isinstance(el, NavigableString) and not el.strip()) or (
        isinstance(el, Tag) and el.name in ALLOW_EMPTY_ELEMENTS
    )


def _remove_trailing_allowed_empty_recursive(tag: Tag):
    """
    Remove trailing allowed empty elements recursively from a tag.

    Args:
        tag (Tag): The tag to process.

    Returns:
        list: The contents after removal.
    """
    for child in tag.find_all(recursive=False):
        if isinstance(child, Tag):
            _remove_trailing_allowed_empty_recursive(child)
        elif isinstance(child, NavigableString) and child.strip() == "":
            child.extract()

    contents = list(tag.contents)
    while (
        contents
        and isinstance(contents[-1], Tag)
        and contents[-1].name in ALLOW_EMPTY_ELEMENTS
    ):
        contents[-1].decompose()
        contents = list(tag.contents)
    return contents


def _remove_empty_tags(soup: BeautifulSoup):
    """
    Remove all empty tags from the soup, except allowed empty elements.

    Args:
        soup (BeautifulSoup): The soup to process.
    """
    # Remove all empty tags (excluding allowed empty elements)
    for element in list(soup.find_all()):
        if isinstance(element, Tag | NavigableString) and is_empty(element):
            element.decompose()

    # Clean up paragraphs
    for p in list(soup.find_all("p")):
        if not isinstance(p, Tag):
            continue
        contents: list[PageElement] = list(p.contents) if isinstance(p, Tag) else []

        # Remove ignorable leading content
        while contents and is_ignorable(contents[0]):
            contents[0].extract()
            contents = list(p.contents) if isinstance(p, Tag) else []

        contents = _remove_trailing_allowed_empty_recursive(p)

        # Remove paragraph if now empty
        if not any(c for c in contents if not is_ignorable(c)):
            p.decompose()


def _wrap_all_paragraphs(soup: BeautifulSoup, block_level_tags: Iterable[str]):
    """
    Wrap all paragraphs in the soup, splitting as needed by block-level tags.

    Args:
        soup (BeautifulSoup): The soup to process.
        block_level_tags (Iterable[str]): Block-level tags to split by.
    """
    for p_tag in list(soup.find_all("p")):
        if not isinstance(p_tag, Tag):
            continue
        new_elements = _split_paragraph(p_tag, block_level_tags)
        if new_elements:
            p_tag.insert_after(*new_elements)
            p_tag.decompose()


def _get_root_soup(tag: Tag) -> BeautifulSoup:
    """
    Get the root BeautifulSoup object for a tag.

    Args:
        tag (Tag): The tag to find the root for.

    Returns:
        BeautifulSoup: The root soup object.
    """
    parent = tag
    while parent is not None and not isinstance(parent, BeautifulSoup):
        parent = parent.parent
    if parent is None:
        raise ValueError("Could not find root BeautifulSoup object")
    return parent


def _split_paragraph(p_tag: Tag, block_level_tags: Iterable[str]) -> list[Tag]:
    """
    Split a paragraph tag into multiple paragraphs by block-level tags.

    Args:
        p_tag (Tag): The paragraph tag to split.
        block_level_tags (Iterable[str]): Block-level tags to split by.

    Returns:
        list[Tag]: List of new paragraph tags.
    """
    soup = _get_root_soup(p_tag)
    new_elements: list[Tag] = []
    buffer: list[Tag] = []

    def flush_buffer():
        if buffer:
            p = soup.new_tag("p")
            for item in buffer:
                p.append(item)
            new_elements.append(p)
            buffer.clear()

    for child in list(p_tag.contents):
        if isinstance(child, Tag) and child.name in block_level_tags:
            if child.name == "img" and not child.get("src"):
                continue
            flush_buffer()
            p = soup.new_tag("p")
            p.append(child)
            new_elements.append(p)
        else:
            buffer.append(child)

    flush_buffer()
    return new_elements


def parse_source(
    source: str,
    filter_: bool = True,
    group: bool = True,
    normalize: bool = True,
    block_level_tags: Iterable[str] = (),
) -> Tag:
    """
    Parse HTML source and return a normalized soup object.

    Args:
        source (str): The HTML source to parse.
        filter_ (bool, optional): Whether to filter children. Defaults to True.
        group (bool, optional): Whether to group inline elements. Defaults to True.
        normalize (bool, optional): Whether to normalize HTML. Defaults to True.
        block_level_tags (Iterable[str], optional): Block-level tags. Defaults to ().

    Returns:
        Tag: The parsed and normalized soup object.

    Example::

        soup = parse_source('<p>Hello <b>world</b></p>')
    """
    # Remove linebreaks from the end of the source
    source = source.strip()
    soup = BeautifulSoup(source, features="html.parser")
    if normalize:
        soup = _normalize_html(soup, block_level_tags)
    if filter_:
        soup = _filter_children(soup)
    if group:
        soup = _group_inline_elements(soup)
    return soup


def all_children(
    element: PageElement | Tag, allow_tags: list[str] | None = None
) -> list[PageElement]:
    """
    Return a list of all children of an element, optionally filtered by tag names.

    Args:
        element (PageElement | Tag): The element to get children from.
        allow_tags (list[str], optional): List of tag names to include.
                                          Defaults to None.

    Returns:
        list[PageElement]: List of child elements.
    """
    raw_children: list[PageElement] = list(getattr(element, "children", []))
    if allow_tags:
        children = [
            child
            for child in raw_children
            if getattr(child, "name", None) in allow_tags
        ]
    else:
        children = raw_children
    return children


def styles(element: Tag) -> dict:
    """
    Parse style attributes from an element into a dictionary.

    Args:
        element (Tag): The element to parse styles from.

    Returns:
        dict: Dictionary of style properties.
    """
    styles = {}
    raw_styles = str(element.get("style", "")).split(";")
    for raw_item in raw_styles:
        item = [i.strip() for i in raw_item.split(":")]
        if len(item) != 2:
            # Malformed style info
            continue
        styles[item[0]] = item[1]
    return styles


def css_classes(element: Tag) -> list[str]:
    """
    Return a list of CSS classes from an element.

    Args:
        element (Tag): The element to get classes from.

    Returns:
        list[str]: List of CSS class names.
    """
    attr = element.get("class")
    return attr if isinstance(attr, list) else [str(attr)]


def is_inline(element: PageElement, include_span: bool = False) -> bool:
    """
    Check if an element is considered inline.

    Args:
        element (PageElement): The element to check.
        include_span (bool, optional): Whether to treat span as inline.
                                       Defaults to False.

    Returns:
        bool: True if inline, False otherwise.
    """
    if isinstance(element, NavigableString):
        return True
    if not isinstance(element, Tag):
        return False
    elif include_span and element.name == "span":
        return True
    return element.name in INLINE_ELEMENTS


def extract_rows_and_possible_blocks(
    table_element: Tag, tags_to_extract: list[str]
) -> tuple[list[tuple[Tag, bool]], list[Tag]]:
    """
    Extract rows and possible blocks from a table element.

    Args:
        table_element (Tag): The table element to process.
        tags_to_extract (list[str]): List of tag names to extract.

    Returns:
        tuple[list[tuple[Tag, bool]], list[Tag]]: Rows and extracted blocks.
    """
    unbound_elements = []

    for tag_name in tags_to_extract:
        for match in table_element.find_all(tag_name):
            unbound_elements.append(match.extract())

    rows = []
    for el in table_element.find_all("tr"):
        parent = el.parent
        if isinstance(parent, Tag):
            rows.append((el, parent.name == "thead"))
    return rows, unbound_elements


def table_cell_type(cell: Tag, is_header: bool = False) -> str:
    """
    Get the type of a table cell ('header' or 'data').

    Args:
        cell (Tag): The table cell element.
        is_header (bool, optional): Whether the cell is a header. Defaults to False.

    Returns:
        str: 'header' or 'data'.
    """
    if is_header:
        return "header"
    return "data" if cell.name == "td" else "header"


def extract_plaintext(element: Tag) -> str:
    """
    Extract plaintext from an element, handling lists specially.

    Args:
        element (Tag): The element to extract text from.

    Returns:
        str: The extracted plaintext.
    """
    plaintext = element.text.strip()
    tag_name = element.name
    if tag_name in ("ol", "ul"):
        plaintext = " ".join([c.text.strip() for c in element.children])
    return plaintext


def url_from_iframe(element: Tag) -> str:
    """
    Parse an iframe element and return its src URL.

    Args:
        element (Tag): The iframe element.

    Returns:
        str: The src URL of the iframe.
    """
    src = ""
    if element.name == "iframe":
        src = element.get("src", "")
    return str(src)


def cleanse_url(url: str) -> str:
    """
    Clean up a URL by decoding HTML entities and normalizing.

    Args:
        url (str): The URL to clean.

    Returns:
        str: The cleansed URL.
    """
    raw_url = url.replace("&amp;", "&")
    parsed = parse.urlparse(raw_url)
    return parsed.geturl()
