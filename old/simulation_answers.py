from definitions import ROOT_DIR
from data_process import generate_key, process_email
import responsiveness_logic
from os import listdir
from os.path import isdir, isfile, join
import re
import numpy as np
import plyvel
from gensim.models import KeyedVectors


def empty(_, __):
    pass


class DirIterator:

    def __init__(self, funcf=empty, funcd=empty):
        self.funcf = funcf
        self.funcd = funcd

    def lookup_files(self, path, count):
        for f in listdir(path):
            sub = join(path, f)
            if isfile(sub):
                self.funcf(sub, count)
                count += 1
                if count % 1000 == 0:
                    print(count, sub)
            elif isdir(sub):
                self.funcd(sub, count)
                count = self.lookup_files(sub, count)
        return count


class PreprocessorTemplate:

    def __init__(self, db_dir, funcf=empty, funcd=empty):
        self.db = plyvel.DB(db_dir, create_if_missing=True)
        self.wb = self.db.write_batch()
        self.di = DirIterator(funcf, funcd)
        self.total = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.wb.write()
        self.db.close()

    def process(self, path):
        self.total = self.di.lookup_files(path, 0)


class SimulationAnswerPreprocessor(PreprocessorTemplate):

    def __init__(self, db_dir):
        super().__init__(db_dir, self.write_answer)
        self.total_resp = 0

    def write_answer(self, path, count):
        with open(path, "r") as file:
            try:
                id_desc = file.readline()
                key = generate_key(id_desc)
                file_str = file.read().replace("\n", "")
                if responsiveness_logic.responsive(file_str):
                    print(count, "is responsive")
                    self.total_resp += 1
                    self.wb.put(key, b"T")
                else:
                    self.wb.put(key, b"F")
            except (TypeError, UnicodeDecodeError):
                print(count, "is not a text file")


class FolderPositionIndexer(PreprocessorTemplate):

    def __init__(self, db_dir):
        super().__init__(db_dir, funcd=self.register_index)

    def register_index(self, path, count):
        emptiness_flag = True
        for f in listdir(path):
            sub = join(path, f)
            if isfile(sub):
                emptiness_flag = False
                break
        if not emptiness_flag:
            print(count, path)
            self.wb.put(count.to_bytes(3, "little"), path.encode())


class WordCacheInitializer(PreprocessorTemplate):

    def __init__(self, db_dir, model):
        super().__init__(db_dir, self.cache)
        self.model = model
        self.marker = set()
        self.cached = 0
        self.date = 0
        self.time = 0
        self.url = 0
        self.etc = 0

    def cache(self, path, count):
        with open(path, "r") as file:
            try:
                raw_data = file.readlines()
                data = process_email(raw_data)
                pass_flag = 0
                for i, v in enumerate(data):
                    if pass_flag > 0:
                        pass_flag -= 1
                    elif len(data) > i + 1 and "".join([v, "_", data[i + 1]]) in self.model.wv:
                        pass_flag = 1
                        concatenated = "".join([v, "_", data[i + 1]])
                        if concatenated not in self.marker:
                            self.marker.add(concatenated)
                            self.wb.put(concatenated.encode(), [0.0] + self.model.wv[concatenated])
                            self.cached += 1
                    elif v not in self.marker:
                        if v in self.model.wv:
                            self.marker.add(v)
                            self.wb.put(v.encode(), [0.0] + self.model.wv[v])
                            self.cached += 1
                        elif re.match("^\\d\\d/\\d\\d/\\d{2,4}$", v):
                            self.marker.add(v)
                            f = v.split("/")
                            vector = np.array([0.1, float(int(f[0])), float(int(f[1])), float(int(f[2]))] + [0.0] * 297)
                            vector = vector.astype(np.float32)
                            self.wb.put(v.encode(), vector)
                            self.date += 1
                        elif re.match("^\\d\\d:\\d\\d$", v):
                            self.marker.add(v)
                            f = v.split(":")
                            vector = np.array([0.2, 0.0, float(int(f[0])), float(int(f[1]))] + [0.0] * 297)
                            vector = vector.astype(np.float32)
                            self.wb.put(v.encode(), vector)
                            self.time += 1
                        elif re.match("^\\d\\d:\\d\\d:\\d\\d$", v):
                            self.marker.add(v)
                            f = v.split(":")
                            vector = np.array([0.2, float(int(f[0])), float(int(f[1])), float(int(f[2]))] + [0.0] * 297)
                            vector = vector.astype(np.float32)
                            self.wb.put(v.encode(), vector)
                            self.time += 1
                        elif "com" in v or "www" in v or "co." in v or "http" in v or "net" in v:
                            self.marker.add(v)
                            vector = [-0.1] + np.random.uniform(-0.25, 0.25, 300).astype(np.float32)
                            self.wb.put(v.encode(), vector)
                            self.url += 1
                        else:
                            self.marker.add(v)
                            vector = [-0.2] + np.random.uniform(-0.25, 0.25, 300).astype(np.float32)
                            self.wb.put(v.encode(), vector)
                            self.etc += 1
            except (TypeError, UnicodeDecodeError):
                print(count, "is not a text file")


def run_sap():
    with SimulationAnswerPreprocessor(ROOT_DIR + "\\data\\db\\sim_answers\\") as sap:
        sap.process(ROOT_DIR + "\\data\\maildir")
        print("responsive entries:", sap.total_resp, "out of", sap.total)
    print("simulation processing done!")


def run_fpi():
    with FolderPositionIndexer(ROOT_DIR + "\\data\\db\\folder_pos\\") as fpi:
        fpi.process(ROOT_DIR + "\\data\\maildir")
    print("folder indexing done!")


def run_wci():
    model = KeyedVectors.load_word2vec_format(ROOT_DIR + "\\data\\orig\\googlenews.bin", binary=True)
    with WordCacheInitializer(ROOT_DIR + "\\data\\db\\word_cache\\", model) as wci:
        wci.process(ROOT_DIR + "\\data\\maildir")
        print("cached entries:", wci.cached)
        print("date entries:", wci.date)
        print("time entries:", wci.time)
        print("url entries:", wci.url)
        print("other entries:", wci.etc)
    print("word caching done!")

