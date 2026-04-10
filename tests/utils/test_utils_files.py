from base64 import b64encode
from collective.transmute.utils import files

import pytest


class TestJsonDumps:
    def test_basic_dict(self):
        data = {"a": 1, "b": "text"}
        result = files.json_dumps(data)
        assert isinstance(result, bytes)
        assert b'"a"' in result
        assert b'"b"' in result

    def test_basic_list(self):
        data = [1, 2, 3]
        result = files.json_dumps(data)
        assert isinstance(result, bytes)
        assert result.startswith(b"[")

    def test_nested(self):
        data = {"items": [{"id": 1}, {"id": 2}]}
        result = files.json_dumps(data)
        assert b'"id"' in result


class TestCsvDump:
    async def test_writes_headers(self, tmp_path):
        path = tmp_path / "out.csv"
        await files.csv_dump([], ["a", "b"], path)
        content = path.read_text()
        assert content.splitlines()[0] == "a,b"

    async def test_writes_rows(self, tmp_path):
        path = tmp_path / "out.csv"
        data = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        await files.csv_dump(data, ["a", "b"], path)
        lines = path.read_text().splitlines()
        assert lines[0] == "a,b"
        assert lines[1] == "1,2"
        assert lines[2] == "3,4"

    async def test_returns_path(self, tmp_path):
        path = tmp_path / "out.csv"
        result = await files.csv_dump([], ["a"], path)
        assert result == path


class TestCsvLoader:
    async def test_loads_rows(self, tmp_path):
        path = tmp_path / "in.csv"
        path.write_text("a,b\n1,2\n3,4\n")
        result = await files.csv_loader(path)
        assert result == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]

    async def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.csv"
        path.write_text("a,b\n")
        result = await files.csv_loader(path)
        assert result == []

    async def test_roundtrip(self, tmp_path):
        path = tmp_path / "roundtrip.csv"
        data = [{"x": "hello", "y": "world"}]
        await files.csv_dump(data, ["x", "y"], path)
        result = await files.csv_loader(path)
        assert result == data


class TestCheckPath:
    def test_existing_path(self, tmp_path):
        assert files.check_path(tmp_path) is True

    def test_missing_path(self, tmp_path):
        assert files.check_path(tmp_path / "nope") is False


class TestCheckPaths:
    def test_both_exist(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        assert files.check_paths(src, dst) is True

    def test_src_missing(self, tmp_path):
        dst = tmp_path / "dst"
        dst.mkdir()
        with pytest.raises(RuntimeError, match="does not exist"):
            files.check_paths(tmp_path / "missing", dst)

    def test_dst_missing(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        with pytest.raises(RuntimeError, match="does not exist"):
            files.check_paths(src, tmp_path / "missing")


class TestSortContentFiles:
    def test_sorts_numerically(self, tmp_path):
        unsorted = [
            tmp_path / "10.json",
            tmp_path / "2.json",
            tmp_path / "1.json",
            tmp_path / "100.json",
        ]
        result = files._sort_content_files(unsorted)
        assert [p.name for p in result] == [
            "1.json",
            "2.json",
            "10.json",
            "100.json",
        ]

    def test_already_sorted(self, tmp_path):
        already = [tmp_path / f"{i}.json" for i in range(1, 4)]
        result = files._sort_content_files(already)
        assert [p.name for p in result] == ["1.json", "2.json", "3.json"]


class TestGetSrcFiles:
    def test_separates_metadata_and_content(self, tmp_path):
        (tmp_path / "1.json").write_text("{}")
        (tmp_path / "2.json").write_text("{}")
        (tmp_path / "export_localroles.json").write_text("{}")
        (tmp_path / "errors.json").write_text("{}")
        (tmp_path / "paths.json").write_text("{}")
        result = files.get_src_files(tmp_path)
        metadata_names = sorted(p.name for p in result.metadata)
        content_names = sorted(p.name for p in result.content)
        assert metadata_names == [
            "errors.json",
            "export_localroles.json",
            "paths.json",
        ]
        assert content_names == ["1.json", "2.json"]

    def test_empty_directory(self, tmp_path):
        result = files.get_src_files(tmp_path)
        assert result.metadata == []
        assert result.content == []


class TestJsonReader:
    async def test_reads_json_files(self, tmp_path):
        (tmp_path / "1.json").write_text('{"@id": "/foo", "@type": "Document"}')
        (tmp_path / "2.json").write_text('{"@id": "/bar", "@type": "Folder"}')
        file_list = sorted(tmp_path.glob("*.json"))
        results = []
        async for filename, data in files.json_reader(file_list):
            results.append((filename, data))
        assert len(results) == 2
        assert results[0][0] == "1.json"
        assert results[0][1]["@id"] == "/foo"
        assert results[1][0] == "2.json"
        assert results[1][1]["@type"] == "Folder"


class TestExportBlob:
    async def test_writes_blob_file(self, tmp_path):
        content_path = tmp_path / "content"
        content_path.mkdir()
        # Simulate how the caller provides content_path.parent in blob_path
        (tmp_path).mkdir(exist_ok=True)
        blob = {
            "filename": "sample.txt",
            "data": b64encode(b"hello world").decode("utf-8"),
        }
        result = await files.export_blob("image", blob, content_path, "my-item")
        blob_file = content_path / "image" / "sample.txt"
        assert blob_file.exists()
        assert blob_file.read_bytes() == b"hello world"
        assert "blob_path" in result

    async def test_uses_item_id_when_filename_empty(self, tmp_path):
        content_path = tmp_path / "content"
        content_path.mkdir()
        blob = {
            "filename": "",
            "data": b64encode(b"data").decode("utf-8"),
        }
        await files.export_blob("file", blob, content_path, "fallback-id")
        assert (content_path / "file" / "fallback-id").exists()


class TestRemoveData:
    def test_removes_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        files.remove_data(tmp_path)
        assert list(tmp_path.glob("*")) == []

    def test_removes_directories(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("x")
        files.remove_data(tmp_path)
        assert list(tmp_path.glob("*")) == []

    def test_removes_mixed_content(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "inner.txt").write_text("inner")
        files.remove_data(tmp_path)
        assert list(tmp_path.glob("*")) == []

    def test_empty_path(self, tmp_path):
        # Should not raise
        files.remove_data(tmp_path)
        assert list(tmp_path.glob("*")) == []


class TestJsonDump:
    async def test_writes_file(self, tmp_path):
        path = tmp_path / "out.json"
        data = {"key": "value"}
        result = await files.json_dump(data, path)
        assert result == path
        assert path.exists()
        assert b'"key"' in path.read_bytes()
