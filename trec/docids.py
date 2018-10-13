import os
from definitions import DATA_DIR
from typing import *

FILE = os.path.join(DATA_DIR, "docids-v2.csv")


def doc_ids() -> List[str]:
    with open(FILE) as file:
        return [line.split(",")[0] for line in file.readlines()]


def for_each_doc(func: Callable[[str], Any]) -> None:
    with open(FILE) as file:
        for line in file:
            func(line.split(",")[0])


class Cached:
    def __init__(self):
        with open(FILE) as file:
            self.dict = {line.split(",")[0]: line.split(",")[1].strip() for line in file}

    def find(self, doc_id: str) -> str:
        return self.dict[doc_id]
