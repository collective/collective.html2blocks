from collective.html2blocks import _types as t
from uuid import uuid4


def is_volto_block(block: t.VoltoBlock | t.SlateBlockItem) -> bool:
    """Check if this is a Volto block."""
    return bool(block.get("@type"))


def info_from_blocks(raw_blocks: list[t.VoltoBlock]) -> t.VoltoBlocksInfo:
    blocks = {str(uuid4()): block for block in raw_blocks}
    layout = list(blocks.keys())
    return {"blocks": blocks, "blocks_layout": {"items": layout}}
