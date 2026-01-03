import os
import posixpath
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path


class ExporterBase(ABC):
    def __init__(self, path: str):
        self.path = path

    @abstractmethod
    def add_image(self, file_data: bytes, path: str, filename: str):
        pass

    def close(self):
        """Optional hook for post-processing (like closing a zip)"""
        pass


class RawExporter(ExporterBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.path, exist_ok=True)

    def add_image(self, file_data: bytes, path: str, filename: str):
        output_dir = os.path.join(self.path, path)
        os.makedirs(output_dir, exist_ok=True)
        save_path = posixpath.join(output_dir, filename)
        with open(save_path, 'wb') as f:
            f.write(file_data)


class CBZExporter(ExporterBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.path = str(Path(self.path).with_suffix(".cbz")) # Note: .cbz is just a renamed .zip
        self.archive = zipfile.ZipFile(
            self.path,
            mode="a",
            compression=zipfile.ZIP_DEFLATED
        )

    def add_image(self, file_data: bytes, path: str, filename: str):
        self.archive.writestr(posixpath.join(path, filename), file_data)

    def close(self):
        self.archive.close()
