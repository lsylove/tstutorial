import re
from typing import *


def author_to_zipdir(author: str, fi: str, xml_seq: int=0, xml_fin: int=0) -> str:
    if xml_seq == 0:
        return "edrm-enron-v2_{}-{}_xml.zip".format(author.lower(), fi.lower())
    else:
        return "edrm-enron-v2_{}-{}_xml_{}of{}.zip".format(author.lower(), fi.lower(), xml_seq, xml_fin)


def zipdir_to_author(zip_dir: str) -> Tuple[str, str, int, int]:
    spl = re.split("[-_]", zip_dir)
    if len(spl) == 6:
        return spl[3].title(), spl[4].title(), 0, 0
    else:
        spl2 = re.split("[a-z\\\.]", spl[6])
        spl2 = list(filter(None, spl2))
        spl2 = list(map(lambda s: int(s), spl2))
        return spl[3].title(), spl[4].title(), spl2[0], spl2[1]
