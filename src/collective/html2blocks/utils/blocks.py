from collective.html2blocks._types import VoltoBlocksInfo
from uuid import uuid4


def is_volto_block(block: dict) -> bool:
    """Check if this is a Volto block."""
    return bool(block.get("@type"))


def info_from_blocks(raw_blocks: list[dict]) -> VoltoBlocksInfo:
    blocks = {str(uuid4()): block for block in raw_blocks}
    layout = list(blocks.keys())
    return {"blocks": blocks, "blocks_layout": {"items": layout}}
