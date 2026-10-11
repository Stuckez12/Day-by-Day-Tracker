import shutil
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.utils import delete_folder, sha256_file


class TestSHA256FileUtils:
    def test_success(self, test_file: Path):
        checksum = sha256_file(test_file)

        assert (
            checksum
            == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )

    def test_file_not_found(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            sha256_file(tmp_path / "missing.txt")


class TestDeleteFolderUtils:
    def test_success(self, tmp_path: Path):
        folder = tmp_path / "folder"
        child = folder / "child"
        child.mkdir(parents=True)
        (child / "test.txt").write_bytes(b"hello world")

        delete_folder(folder)

        assert not folder.exists()

    def test_path_not_found(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            delete_folder(tmp_path / "missing.txt")

    def test_raises_when_path_still_exists(self, mocker: MockerFixture, tmp_path: Path):
        folder = tmp_path / "folder"
        folder.mkdir()
        rmtree = mocker.patch.object(shutil, "rmtree")

        with pytest.raises(FileExistsError, match="was not deleted"):
            delete_folder(folder)

        rmtree.assert_called_once_with(folder)
