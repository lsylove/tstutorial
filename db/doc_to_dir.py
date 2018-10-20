import os
from plyvel import destroy_db
from definitions import ROOT_DIR
from .wrappers import PlyvelWrapper

DIR = os.path.join(ROOT_DIR, "data", "db", "d2d")


class Writer(PlyvelWrapper[bytes, bytes]):
    def __init__(self, db_dir: str=DIR):
        super().__init__(db_dir)
        self.stat = 0

    def add(self, key: str, value: str) -> None:
        self.write(key.encode(), value.encode())
        self.stat += 1


class Reader(PlyvelWrapper[bytes, bytes]):
    def __init__(self, db_dir: str=DIR):
        super().__init__(db_dir)

    def find(self, key: str) -> str:
        return self.read(key.encode()).decode("utf-8")

    def open(self, key: str) -> object:
        return open(self.find(key), mode="r", encoding="UTF8")


def destroy(db_dir: str=DIR) -> None:
    destroy_db(db_dir)
