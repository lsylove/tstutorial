from os import path, listdir
from typing import *
from .author import author_to_zipdir


def compose_dir(root_dir: str, author: str, fi: str, text_seq: int=0, xml_seq: int=0, xml_fin: int=0) -> str:
    zip_dir = author_to_zipdir(author, fi, xml_seq, xml_fin)
    sub = "text_{:03d}".format(text_seq)
    return path.join(root_dir, zip_dir, sub)


def compose(root_dir: str, doc_id: str, author: str, fi: str, text_seq: int=0, xml_seq: int=0, xml_fin: int=0) -> str:
    sub = compose_dir(root_dir, author, fi, text_seq, xml_seq, xml_fin)
    return path.join(sub, "".join([doc_id, ".txt"]))


def for_each_file(root_dir: str, func: Callable[[str, str], Any], recursive: bool=True) -> None:
    for p in listdir(root_dir):
        sub = path.join(root_dir, p)
        if path.isfile(sub):
            func(p, sub)
        elif path.isdir(sub) and recursive:
            for_each_file(sub, func)
