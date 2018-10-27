import nltk
import re
from itertools import count
from datetime import datetime
from typing import *


DT_PLACEHOLDER_PROTO = "__dt_placeholder_#"
DT_PLACEHOLDER_HEAD = DT_PLACEHOLDER_PROTO.replace("#", "h")

SYMBOL = "EDRM Enron Email Data Set has been produced in EML, PST and NSF format by ZL Technologies, Inc."
FOOTER = "***********\n" + SYMBOL


def datetime_head(message: str) -> Tuple[str, str, List[str]]:
    cut = message.find("\n")
    ret = " ".join([DT_PLACEHOLDER_HEAD, DT_PLACEHOLDER_HEAD, message[cut:]])
    dt = datetime.strptime(message[6:cut - 6].strip(), "%a, %d %b %Y %H:%M:%S %z")
    return ret, DT_PLACEHOLDER_HEAD, [dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")]


def drop_headers(message: str) -> str:
    cut_b = message.find("X-SDOC:")
    cut_e = message.find(".eml")
    assert cut_b < cut_e
    message = message[:cut_b] + message[cut_e + 5:]
    cut_b = message.find("From:")
    cut_e = message.find("Subject:")
    while cut_b != -1 and cut_e != -1:
        if not cut_b < cut_e:
            temp = cut_b
            cut_b = cut_e
            cut_e = temp
        message = message[:cut_b] + message[cut_e + 9:]
        cut_b = message.find("---")
        cut_e = message.find("Subject:")
    return message[:message.find(FOOTER)]


def drop_tags(message: str) -> str:
    length = len(message)
    match = re.search(r"<[^><]+>", message)
    while match:
        if length < (match.end() - match.start()) * 20:
            pass
        message = message[:match.start()] + message[match.end():]
        match = re.search(r"<[^><]+>", message)
    return message


def simplify(message: str) -> List[str]:
    message = message.lower().replace("-", "_")
    text = [re.sub(r"\d", "#", re.sub(r"[^A-Za-z0-9'_./]+", "", w)) for w in message.split() if w]
    text = [w.split("/") for w in text]
    return [w for l in text for w in l if len(w) and not re.match("^#+$", w)]


def drop_stopwords(text: List[str]) -> List[str]:
    global sw
    return list(filter(lambda w: w not in sw, text))


def drop_url(text: List[str]) -> List[str]:
    return list(filter(lambda w: not (".com" in w or "www" in w or "co." in w or "http" in w or ".net" in w), text))


def remove_period(text: List[str]) -> List[str]:
    text = [w.split(".") for w in text if not re.match(r"^\.*$", w)]
    return [w for l in text for w in l if len(w) and not re.match(r"^[#_]+$", w)]


def recover_datetime(text: List[str], dt: Mapping[str, List[str]]) -> List[str]:
    dt = {k: (count(), v) for k, v in dt.items()}
    return [dt[w][1][next(dt[w][0])] if w in dt else w for w in text]


def lemmatize(text: List[str]) -> List[str]:
    global lz
    return [str(min(lz.lemmatize(w), lz.lemmatize(w, pos="v"), key=len)) for w in text]


def drop_weirdos(text: List[str]) -> List[str]:
    return [w for w in text if len(w) > 2 and not w.startswith("'") and not w.count("#") > 4 and not w.count("_") > 4]


sw = set(nltk.corpus.stopwords.words("english"))
lz = nltk.stem.WordNetLemmatizer()
