from collective.html2blocks._types import VoltoBlockInfo
from uuid import uuid4


def info_from_blocks(raw_blocks: list[dict]) -> VoltoBlockInfo:
    blocks = {str(uuid4()): block for block in raw_blocks}
    layout = list(blocks.keys())
    return {"blocks": blocks, "blocks_layout": {"items": layout}}
