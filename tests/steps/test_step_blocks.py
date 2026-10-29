from collective.transmute.settings import get_settings
from collective.transmute.steps.blocks import process_blocks

import asyncio
import pytest


HTML = "<p>Intro</p><pre><code>print(1)</code></pre>"


@pytest.fixture
def convert(test_dir):
    def func(converter_table: str | None) -> list[str]:
        if converter_table is not None:
            path = test_dir / "transmute.toml"
            path.write_text(
                path.read_text() + f"\n[steps.blocks.converter]\n{converter_table}\n"
            )
        settings = get_settings(test_dir)
        item = {"@type": "Document", "title": "Test", "text": {"data": HTML}}

        async def run():
            async for result in process_blocks(item, None, settings):
                return result

        result = asyncio.run(run())
        return list(result["blocks"].values())

    return func


def test_converter_default_keeps_pre_as_slate(convert):
    types = [block["@type"] for block in convert(None)]
    assert "codeBlock" not in types
    assert "slate" in types


def test_converter_enables_code_block(convert):
    types = [block["@type"] for block in convert("codeBlock = true")]
    assert "codeBlock" in types
    assert "slate" in types


def test_converter_passes_options(convert):
    blocks = convert('codeBlock = { style = "light" }')
    code_blocks = [block for block in blocks if block["@type"] == "codeBlock"]
    assert len(code_blocks) == 1
    assert code_blocks[0]["style"] == "light"
