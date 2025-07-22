from collective.html2blocks import _types as t


def item_generator(
    gen: t.SlateItemGenerator, filter_none: bool = True
) -> t.SlateItemGenerator:
    """Yield from a generator."""
    try:
        while True:
            item = next(gen)
            if not filter_none or item is not None:
                yield item
    except StopIteration as e:
        return e.value
