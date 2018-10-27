import db.doc_to_dir
import db.attachment_type
import db.word_to_vector
import directories.general
import documents.attachment
import documents.message
import trec.docids
import sys
from definitions import *
from typing import *


class MaxLenReached(Exception):
    pass


def construct_doc_to_dir(max_len: int) -> None:
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
                print(reference["total"], "Files Processed")
                if reference["total"] >= max_len:
                    raise MaxLenReached
        try:
            directories.general.for_each_file(EDRM_DIR, append_kv)
        finally:
            print("Total # of Files:", reference["total"])


def construct_attachment_type(max_len: int) -> None:
    cached = trec.docids.Cached()
    doc_ids = trec.docids.doc_ids()
    doc_ids = {cached.find(did) for did in doc_ids}
    reference = {
        "total": 0,
        "attachments": 0,
        "fwa": 0,
        "fake": 0
    }
    prev_marker = [False]
    with db.attachment_type.Writer() as writer:
        def append_kv(doc_file, file_dir):
            doc_id = directories.general.doc_file_to_doc_id(doc_file)
            reference["total"] += 1
            if reference["total"] % 10000 == 0:
                print(reference["total"], "Files Processed")
                if reference["total"] >= max_len:
                    raise MaxLenReached
            if documents.attachment.is_attachment(doc_id):
                prev_marker[0] = True
                return
            elif not prev_marker[0]:
                return
            prev_marker[0] = False
            reference["fwa"] += 1
            with open(file_dir, encoding="utf-8") as file:
                types = documents.attachment.parse_attachment_types(file)
                for i, v in enumerate(types):
                    attachment_id = ".".join([doc_id, str(i + 1)])
                    if attachment_id in doc_ids:
                        writer.add(attachment_id, v)
                        reference["attachments"] += 1
                    else:
                        reference["fake"] += 1
        try:
            directories.general.for_each_file(EDRM_DIR, append_kv)
        finally:
            print("Total # of Files:", reference["total"])
            print("Total # of Files with Attachments:", reference["fwa"])
            print("Total # of Attachments:", reference["attachments"])
            print("Total # of Invalid Attachments:", reference["fake"])


def construct_word2vec(max_len: int) -> None:
    reference = {
        "total": 0
    }
    model = db.word_to_vector.default_model()
    with db.word_to_vector.Writer(model) as writer:
        def append_kv(doc_file, file_dir):
            doc_id = directories.general.doc_file_to_doc_id(doc_file)
            reference["total"] += 1
            if reference["total"] % 2000 == 0:
                print(reference["total"], "Files Processed")
                if reference["total"] >= max_len:
                    raise MaxLenReached
            with open(file_dir, "r", encoding="utf-8") as file:
                if documents.attachment.is_attachment(doc_id):
                    text = documents.attachment.process(file)
                else:
                    text = documents.message.process(file)
            writer.add(text)
        try:
            directories.general.for_each_file(EDRM_DIR, append_kv)
        finally:
            print("Total # of Files:", reference["total"])
            print("Total # of Cached Entries from Model: ", len(writer.markerA))
            print("Total # of Cached Datetime Entries: ", len(writer.markerB))
            print("Total # of Cached Entries not within Model: ", len(writer.markerC))
            print("Total # of Cached Entries from Model (Non-Unique): ", writer.statA)
            print("Total # of Cached Datetime Entries (Non-Unique): ", writer.statB)
            print("Total # of Cached Entries not within Model (Non-Unique): ", writer.statC)


def destroy_doc_to_dir(_: int) -> None:
    db.doc_to_dir.destroy()


def destroy_attachment_type(_: int) -> None:
    db.attachment_type.destroy()


def destroy_word2vec(_: int) -> None:
    db.word_to_vector.destroy()


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        raise ValueError("Too few arguments")
    try:
        {
            "wv": construct_word2vec,
            "dd": construct_doc_to_dir,
            "at": construct_attachment_type,
            "xwv": destroy_word2vec,
            "xdd": destroy_doc_to_dir,
            "xat": destroy_attachment_type
        }[argv[1]](int(argv[2]) if len(argv) > 2 else sys.maxsize)
    except KeyError:
        raise ValueError("Invalid argument #0")
    except ValueError:
        raise ValueError("Invalid argument #1")
    except MaxLenReached:
        pass


if __name__ == "__main__":
    main(sys.argv)
