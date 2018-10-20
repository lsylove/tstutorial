import plyvel
from typing import *

K = TypeVar("K")
V = TypeVar("V")


class PlyvelWrapper(Generic[K, V]):
    def __init__(self, db_dir):
        self.db = plyvel.DB(db_dir, create_if_missing=True)
        self.wb = self.db.write_batch()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self.wb.write()
        self.db.close()

    def write(self, key: K, value: V) -> None:
        self.wb.put(key, value)

    def read(self, key: K) -> Optional[V]:
        return self.db.get(key)
