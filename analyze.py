import db.doc_to_dir
import db.attachment_type
import db.word_to_vector
import db.attachment_type
import documents.attachment
import documents.message
import trec.seed
import trec.formatter
import trec.docids
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


def identify_seed_type(req_id: int) -> None:
    """
    Identifies attachment types for seeded documents.
    :param req_id: request id for seeds to be analyzed
    :return: None
    """
    seeds = trec.seed.seeds(req_id)
    res1 = set()
    res2 = set()
    with db.attachment_type.Reader() as reader:
        for obj in seeds:
            doc_id = obj["doc_id"]
            if documents.attachment.is_attachment(doc_id):
                try:
                    attachment_type = reader.find(doc_id)
                    if obj["relevance"] == 1:
                        res1.add(attachment_type)
                    else:
                        res2.add(attachment_type)
                except AttributeError:
                    print(doc_id)
    print("Attachment Types for Relevant Documents: ")
    for res in res1:
        print(res)
    print("Attachment Types for Non-Relevant Documents: ")
    for res in res2:
        print(res)


def mock_submission() -> None:
    """
    Creates mock submission file
    :return: None
    """
    cached = trec.docids.Cached()
    doc_ids = trec.docids.doc_ids()
    doc_ids = sorted([cached.find(doc_id) for doc_id in doc_ids])
    with open(os.path.join(TEMP_DIR, "mock.txt"), "w", encoding="utf-8") as file:
        for req_id in range(200, 201):
            lst = [{
                "req_id": req_id,
                "doc_id": doc_id,
                "estimate": 0
            } for doc_id in doc_ids]
            lst = trec.formatter.format_object_array(lst)
            line = "\n".join(lst)
            file.write(line + "\n")


def check_longest_data(req_id: int) -> None:
    """
    check longest data among seed documents for req_id. also prints individual data
    :param req_id: request id for seeds to be analyzed
    :return: None
    """
    ref = [0]
    with db.word_to_vector.Reader() as reader_w2v:
        with db.doc_to_dir.Reader() as reader_d2d:
            with db.attachment_type.Reader() as reader_at:
                def vectorize(doc_id):
                    ref[0] += 1
                    if ref[0] % 20 == 0:
                        print("So far,", ref[0], "documents processed")
                    with reader_d2d.open(doc_id) as file:
                        if documents.attachment.is_attachment(doc_id):
                            text = documents.attachment.process(file)
                            try:
                                attachment_type = reader_at.find(doc_id)
                                if attachment_type == "application/msexcell":
                                    seen = set()
                                    text = [w for w in text if not (w in seen or seen.add(w))]
                            except AttributeError:
                                pass
                        else:
                            text = documents.message.process(file)
                    ret = reader_w2v.lookup_embedding(text)
                    print(doc_id, ret.shape)
                    return ret
                cached = trec.seed.Cached()
                lst = cached.seeds(req_id)
                longest = max(((vectorize(obj["doc_id"]).shape[0], obj["doc_id"]) for obj in lst),
                              key=lambda tup: tup[0])
                print("Longest seed for", req_id, "is", longest)


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
    elif argv[1] == "is":
        identify_seed_type(int(argv[2]))
    elif argv[1] == "ms":
        mock_submission()
    elif argv[1] == "cl":
        check_longest_data(int(argv[2]))
    else:
        raise ValueError("Invalid argument #0")


if __name__ == "__main__":
    main(sys.argv)
