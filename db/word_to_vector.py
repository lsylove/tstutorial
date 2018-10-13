import os
import re
import numpy as np
from datetime import datetime
from gensim.models import KeyedVectors
from plyvel import destroy_db
from definitions import ROOT_DIR, DATA_DIR
from typing import *
from .wrappers import PlyvelWrapper

DIR = os.path.join(ROOT_DIR, "data", "db", "w2v")
W2V_FILE = os.path.join(DATA_DIR, "googlenews.bin")


class Writer(PlyvelWrapper[bytes, np.ndarray]):
    def __init__(self, model: Mapping[str, np.ndarray], db_dir: str=DIR):
        super().__init__(db_dir)
        self.model = model
        self.markerA = set()
        self.markerB = set()
        self.markerC = set()
        self.statA = 0
        self.statB = 0
        self.statC = 0
        for k, _ in self.db:
            self.markerA.add(k)

    def add(self, keys: List[str]) -> None:
        for i, k in enumerate(keys):
            if len(keys) > i + 1:
                for elt in ["".join([k, "_", keys[i + 1]]), "".join([k, "_", keys[i + 1]]).title()]:
                    if elt in self.model:
                        if elt not in self.markerA:
                            v = self.model[elt]
                            v = np.insert(v, 0, [0.])
                            self.write(elt.encode(), v)
                            self.markerA.add(elt)
                        self.statA += 1
            if k in self.markerA:
                self.statA += 1
                continue
            elif k in self.markerB:
                self.statB += 1
                continue
            elif k in self.markerC:
                self.statC += 1
                continue
            try:
                v = self.model[k]
                v = np.insert(v, 0, [0.])
                self.write(k.encode(), v)
                self.markerA.add(k)
                self.statA += 1
            except KeyError:
                v = compose_datetime_vector(k)
                if v is not None:
                    self.write(k.encode(), v)
                    self.markerB.add(k)
                    self.statB += 1
                else:
                    vector = np.random.uniform(-0.25, 0.25, 300).astype(np.float32)
                    vector = np.insert(vector, 0, [-0.1])
                    self.write(k.encode(), vector)
                    self.markerC.add(k)
                    self.statC += 1


class Reader(PlyvelWrapper[bytes, np.ndarray]):
    def __init__(self, db_dir: str=DIR):
        super().__init__(db_dir)

    def find(self, key: str) -> np.ndarray:
        return self.read(key.encode())


def compose_datetime_vector(line: str) -> Optional[np.ndarray]:
    if re.match("^\d\d/\d\d/\d{2,4}$", line):
        date = datetime.strptime(line, "%d/%m/%Y")
        degree = date.timestamp() / 2524608000 - 0.5
        vector = np.array([0.1, degree] + [0.] * 299)
        return vector.astype(np.float32)
    elif re.match("^\d\d-\d\d-\d{2,4}$", line):
        date = datetime.strptime(line, "%d-%m-%Y")
        degree = date.timestamp() / 2524608000 - 0.5
        vector = np.array([0.1, degree] + [0.] * 299)
        return vector.astype(np.float32)
    elif re.match("^\d\d:\d\d$", line) or re.match("^\d\d:\d\d:\d\d$", line):
        lst = line.split(":")
        lst.append("0")
        time = int(lst[0]) * 3600 + int(lst[1]) * 60 + int(lst[2])
        degree = time / 172800 - 0.25
        vector = np.array([0.2, degree] + [0.] * 299)
        return vector.astype(np.float32)
    else:
        return None


def default_model(model_dir: str=W2V_FILE) -> Mapping[str, np.ndarray]:
    return KeyedVectors.load_word2vec_format(model_dir, binary=True).wv


def destroy(db_dir: str=DIR) -> None:
    destroy_db(db_dir)
