import db.doc_to_dir
import trec.seed
import directories.general
import sys
import re
from shutil import copyfile
from definitions import *
from typing import *


def open_file(doc_id: str) -> None:
    """
    Opens a specific file and prints its content to console.
    Args: of <doc_id>
    :param doc_id: document id of the file to be opened
    :return: None
    """
    with db.doc_to_dir.Reader() as reader:
        with reader.open(doc_id) as file:
            for line in file:
                print(line.strip())


def export_seeds(req_id: int, relevance: int=1, export_dir: str=None) -> None:
    """
    Exports seeds specified by request id and relevance to a directory.
    Args: es <req_id> [<relevance>]
    :param req_id: request id for seeds to be exported
    :param relevance: relevance filter (default 1)
    :param export_dir: export directory under "/data/temp"
    :return: None
    """
    if export_dir is None:
        export_dir = "_".join([str(req_id), str(relevance)])
    export_dir = os.path.join(TEMP_DIR, export_dir)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    seeds = trec.seed.seeds(req_id)
    seeds = filter(lambda ob: ob["relevance"] == relevance, seeds)
    with db.doc_to_dir.Reader() as reader:
        for obj in seeds:
            doc_id = obj["doc_id"]
            doc_dir = reader.find(doc_id)
            dst = os.path.join(export_dir, "".join([doc_id, ".txt"]))
            copyfile(doc_dir, dst)


def attachment_types(root_dir: str=EDRM_DIR) -> None:
    """
    Identifies existent attachment types throughout the dataset.
    Args: at <any_thing>
    :param root_dir: optional root directory to start recursive search (default root)
    :return: None
    """
    types = set()
    reference = {
        "total": 0
    }
    symbol = "EDRM Enron Email Data Set has been produced in EML, PST and NSF format by ZL Technologies, Inc."

    def identify(doc_file: str, file_dir: str) -> None:
        reference["total"] += 1
        if reference["total"] % 2000 == 0:
            print(reference["total"], "Files Processed")
        if re.match("^.*\d+\.txt$", doc_file):
            return
        with open(file_dir, mode="r", encoding="utf-8") as file:
            foot_check = False
            for line in file:
                if not foot_check and not line.startswith(symbol):
                    continue
                foot_check = True
                if line.startswith("Attachment:"):
                    try:
                        spl = line.split("=")
                        v = spl[len(spl) - 1].strip()
                        if v not in types:
                            print("Type:", v)
                            print("Type From:", doc_file)
                            types.add(v)
                    except IndexError:
                        print("Exception Line:", line.strip())
                        print("Exception File:", doc_file)
    directories.general.for_each_file(root_dir, identify)
    print("Total # of Files:", reference["total"])
    print("Identified Types:")
    for typ in types:
        print(typ)


def main(argv: List[str]) -> None:
    if len(argv) < 3:
        raise ValueError("Too few arguments")
    if argv[1] == "of":
        open_file(argv[2])
    elif argv[1] == "es":
        if len(argv) == 3:
            export_seeds(int(argv[2]))
        else:
            export_seeds(int(argv[2]), int(argv[3]))
    elif argv[1] == "at":
        attachment_types()
    else:
        raise ValueError("Invalid argument #0")


if __name__ == "__main__":
    main(sys.argv)
