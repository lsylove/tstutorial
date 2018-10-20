import db.doc_to_dir
import directories.general
import sys
from definitions import *
from typing import *


def construct_word2vec():
    pass


def construct_doc_to_dir():
    reference = {
        "total": 0
    }
    with db.doc_to_dir.Writer() as writer:
        def append_kv(doc_file, file_dir):
            doc_file = doc_file.split(".")
            del doc_file[-1]
            writer.add(".".join(doc_file), file_dir)
            reference["total"] += 1
            if reference["total"] % 10000 == 0:
                print(reference["total"], "files are processed")
        directories.general.for_each_file(EDRM_DIR, append_kv)
        print("Total # of Files:", reference["total"])


def main(argv: List[str]):
    if len(argv) < 2:
        raise ValueError("Too few arguments")
    if argv[1] == "dd":
        construct_doc_to_dir()
    elif argv[1] == "wv":
        construct_word2vec()
    else:
        raise ValueError("Invalid argument #0")


if __name__ == "__main__":
    main(sys.argv)
