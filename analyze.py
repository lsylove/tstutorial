import db.doc_to_dir
import trec.seed
import sys
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
    else:
        raise ValueError("Invalid argument #0")


if __name__ == "__main__":
    main(sys.argv)
