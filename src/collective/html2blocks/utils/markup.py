from .inline import ALLOW_EMPTY_ELEMENTS
from .inline import INLINE_ELEMENTS
from bs4 import BeautifulSoup
from bs4.element import Comment
from bs4.element import NavigableString
from collections.abc import Iterable
from collective.html2blocks._types import Element
from collective.html2blocks._types import Tag
from urllib import parse


def _group_inline_elements(soup: BeautifulSoup) -> Element:
    """Group inline elements."""
    wrapper = None
    children = list(soup.children)
    for element in children:
        inline_element = is_inline(element, True)
        if inline_element and not wrapper:
            wrapper = soup.new_tag("p")
            element.insert_before(wrapper)
            wrapper.append(element.extract())
        elif inline_element:
            wrapper.append(element.extract())
        elif not inline_element and wrapper:
            if wrapper.text == "\n":
                wrapper.extract()
            wrapper = None
    return soup


def _filter_children(soup: BeautifulSoup) -> BeautifulSoup:
    """Return a list of all top level children of soup.

    Filtering Comment and empty elements.
    """
    children = list(soup.children)
    for child in children:
        if isinstance(child, Comment) or (
            isinstance(child, NavigableString) and child.text == "\n"
        ):
            child.extract()
    children = list(soup.children)
    if len(children) == 1 and children[0].name == "div":
        # If there is only a wraping div, return its children
        new_soup = BeautifulSoup("", features="html.parser")
        internal_ = list(children[0].children)
        for child in internal_:
            child = child.extract()
            new_soup.append(child)
        soup = _filter_children(new_soup)
    return soup


def _normalize_html(soup: BeautifulSoup, block_level_tags: Iterable[str] = ()):
    _recursively_simplify(soup)
    _remove_empty_tags(soup)
    _wrap_all_paragraphs(soup, block_level_tags)
    return soup


def _recursively_simplify(tag: Tag):
    for child in list(tag.children):
        if isinstance(child, Tag):
            _recursively_simplify(child)

    if (
        isinstance(tag, Tag)
        and len(tag.contents) == 1
        and isinstance(tag.contents[0], Tag)
    ):
        child = tag.contents[0]
        if tag.name == child.name and tag.attrs == child.attrs:
            tag.replace_with(child)
            _recursively_simplify(child)


def is_empty(tag: Tag) -> bool:
    return (
        tag.name not in ALLOW_EMPTY_ELEMENTS
        and not tag.contents
        and not tag.string
        and not tag.attrs
    )


def is_ignorable(el) -> bool:
    return (isinstance(el, NavigableString) and not el.strip()) or (
        isinstance(el, Tag) and el.name in ALLOW_EMPTY_ELEMENTS
    )


def _remove_empty_tags(soup: BeautifulSoup):
    def remove_trailing_allowed_empty_recursive(tag: Tag):
        for child in tag.find_all(recursive=False):
            if isinstance(child, Tag):
                remove_trailing_allowed_empty_recursive(child)

        contents = list(tag.contents)
        while (
            contents
            and isinstance(contents[-1], Tag)
            and contents[-1].name in ALLOW_EMPTY_ELEMENTS
        ):
            contents[-1].decompose()
            contents = list(tag.contents)

    # Remove all empty tags (excluding allowed empty elements)
    for tag in list(soup.find_all()):
        if is_empty(tag):
            tag.decompose()

    # Clean up paragraphs
    for p in list(soup.find_all("p")):
        contents = list(p.contents)

        # Remove ignorable leading content
        while contents and is_ignorable(contents[0]):
            contents[0].extract()
            contents = list(p.contents)

        remove_trailing_allowed_empty_recursive(p)

        # Remove paragraph if now empty
        if not any(c for c in p.contents if not is_ignorable(c)):
            p.decompose()


def _wrap_all_paragraphs(soup: BeautifulSoup, block_level_tags: Iterable[str]):
    for p_tag in list(soup.find_all("p")):
        new_elements = _split_paragraph(p_tag, block_level_tags)
        if new_elements:
            p_tag.insert_after(*new_elements)
            p_tag.decompose()


def _get_root_soup(tag: Tag) -> BeautifulSoup:
    parent = tag
    while parent is not None and not isinstance(parent, BeautifulSoup):
        parent = parent.parent
    if parent is None:
        raise ValueError("Could not find root BeautifulSoup object")
    return parent


def _split_paragraph(p_tag: Tag, block_level_tags: Iterable[str]) -> list[Tag]:
    soup = _get_root_soup(p_tag)
    new_elements = []
    buffer = []

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
) -> Element:
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
    element: Element | Tag, allow_tags: list[str] | None = None
) -> list[Element | Tag]:
    """Return a list of all children of an element."""
    raw_children: list[Element | Tag] = list(getattr(element, "children", []))
    if allow_tags:
        chilren = [
            child
            for child in raw_children
            if getattr(child, "name", None) in allow_tags
        ]
    else:
        chilren = raw_children
    return chilren


def styles(element: Element) -> dict:
    """Parse style attributes in an element."""
    styles = {}
    raw_styles = element.get("style", "").split(";")
    for item in raw_styles:
        item = [i.strip() for i in item.split(":")]
        if len(item) != 2:
            # Malformed style info
            continue
        styles[item[0]] = item[1]
    return styles


def css_classes(element: Element) -> list[str]:
    """Return a list of css classes in an element."""
    return element.get("class", [])


def is_inline(element: Element, include_span: bool = False) -> bool:
    """Validate if element is inline."""
    if isinstance(element, NavigableString):
        return True
    if include_span and element.name == "span":
        return True
    return element.name in INLINE_ELEMENTS


def extract_rows_and_possible_blocks(
    table_element: Tag, tags_to_extract: list[str]
) -> tuple[list[tuple[Element, bool]], list[Element]]:
    """Clean up table and return rows and possible blocks."""
    unbound_elements = []

    for tag_name in tags_to_extract:
        for match in table_element.find_all(tag_name):
            unbound_elements.append(match.extract())

    rows = []
    for el in table_element.find_all("tr"):
        parent = el.parent
        rows.append((el, parent.name == "thead"))
    return rows, unbound_elements


def table_cell_type(cell: Element, is_header: bool = False) -> str:
    if is_header:
        return "header"
    return "data" if cell.name == "td" else "header"


def extract_plaintext(element: Element) -> str:
    plaintext = element.text.strip()
    tag_name = element.name
    if tag_name in ("ol", "ul"):
        plaintext = " ".join([c.text.strip() for c in element.children])
    return plaintext


def url_from_iframe(element: Element) -> str:
    """Parse an iframe element and return the cleansed url."""
    src = ""
    if element.name == "iframe":
        src = element.get("src", "")
    return src


def cleanse_url(url: str) -> str:
    """Clean up url."""
    raw_url = url.replace("&amp;", "&")
    parsed = parse.urlparse(raw_url)
    return parsed.geturl()
