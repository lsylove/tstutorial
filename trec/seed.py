import os
from definitions import DATA_DIR
from typing import *

FILE = os.path.join(DATA_DIR, "seed.csv")


def seeds(req_id: int) -> List[Mapping[str, Any]]:
    with open(FILE) as file:
        return [dict(req_id=req_id, doc_id=line.split(",")[3].strip(), relevance=int(line.split(",")[2]))
                for line in file if int(line.split(",")[1]) == req_id]


def all_seeds() -> List[Mapping[str, Any]]:
    with open(FILE) as file:
        return [dict(req_id=int(line.split(",")[1]), doc_id=line.split(",")[3].strip(), relevance=int(line.split(",")[2]))
                for line in file]


class Cached:
    def __init__(self):
        self.lst = []
        with open(FILE) as file:
            for line in file:
                spl = line.strip().split(",")
                try:
                    self.lst[int(spl[1])][spl[3]] = int(spl[2])
                except IndexError:
                    self.lst.insert(int(spl[1]), {spl[3]: int(spl[2])})

    def seeds(self, req_id: int) -> List[Mapping[str, Any]]:
        return [dict(req_id=req_id, doc_id=k, relevance=v) for k, v in self.lst[req_id].items()]

    def seed_object(self, doc_id: str) -> Optional[Mapping[str, Any]]:
        for (i, dic) in enumerate(self.lst):
            if doc_id in dic:
                return dict(req_id=i, doc_id=doc_id, relevance=dic[doc_id])
        return None
