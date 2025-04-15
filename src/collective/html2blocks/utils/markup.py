from .inline import INLINE_ELEMENTS
from bs4 import BeautifulSoup
from bs4.element import Comment
from bs4.element import NavigableString
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


def parse_source(source: str, filter_: bool = True, group: bool = True) -> Element:
    # Remove linebreaks from the end of the source
    source = source.strip()
    soup = BeautifulSoup(source, features="html.parser")
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


def extract_table_rows(element: Element) -> list[tuple[Element, bool]]:
    rows = []
    for el in element.find_all("tr"):
        parent = el.parent
        rows.append((el, parent.name == "thead"))
    return rows


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
