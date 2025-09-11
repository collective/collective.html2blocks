"""
Generator utility for iterating over Slate item generators.

This module provides helpers for consuming generator-based block conversion
functions, filtering out None values, and returning final results.

Example usage::

    from collective.html2blocks.utils.generator import item_generator

    def my_gen():
        yield {'type': 'p', 'children': []}
        yield None
        yield {'type': 'h1', 'children': []}
        return 'done'

    result = list(item_generator(my_gen(), filter_none=True))
"""

from collective.html2blocks import _types as t


def item_generator(
    gen: t.SlateItemGenerator, filter_none: bool = True
) -> t.SlateItemGenerator:
    """
    Yield items from a SlateItemGenerator, optionally filtering out None values.

    This function consumes a generator, yielding each item. If filter_none is True,
    None values are skipped. When the generator is exhausted, the return value is
    returned from the StopIteration exception.

    Args:
        gen (SlateItemGenerator): The generator to consume.
        filter_none (bool, optional): If True, skip None values. Defaults to True.

    Yields:
        SlateBlockItem: Each item produced by the generator.

    Returns:
        Any: The value returned by the generator when exhausted.

    Example::

        def my_gen():
            yield {'type': 'p', 'children': []}
            yield None
            yield {'type': 'h1', 'children': []}
            return 'done'

        result = list(item_generator(my_gen(), filter_none=True))
    """
    try:
        while True:
            item = next(gen)
            if not filter_none or item is not None:
                yield item
    except StopIteration as e:
        return e.value
