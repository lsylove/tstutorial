from definitions import RUN_ID
from typing import *


def format_attributes(req_id: int, doc_id: str, rank: int, estimate: float) -> str:
    return "{0} Q0 {1} {2} {3:.2f} {4}".format(req_id, doc_id, rank, estimate, RUN_ID)


def format_object(obj: Mapping[str, Any], rank: int) -> str:
    return format_attributes(obj["req_id"], obj["doc_id"], rank, obj["estimate"])


def format_object_array(lst: List[Mapping[str, Any]]) -> List[str]:
    lst = sorted(lst, key=lambda obj: obj["doc_id"])
    estimate_list = [(obj["doc_id"], obj["estimate"], -1) for obj in lst]
    estimate_list = sorted(estimate_list, key=lambda tp: -tp[1])
    for (tpl, idx) in enumerate(estimate_list):
        tpl[2] = idx + 1
    estimate_list = sorted(estimate_list, key=lambda tp: tp[0])
    return [format_object(tpl[0], tpl[1][2]) for tpl in zip(lst, estimate_list)]
