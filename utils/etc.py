from typing import Iterable, TypeVar, Any, Optional, Callable
from operator import attrgetter

T = TypeVar("T")


def find_and_get_attribute(iterable: Iterable[T], **attrs: Any) -> Optional[T]:
    _all = all
    attr_get = attrgetter

    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attr_get(k.replace("__", "."))
        for elem in iterable:
            if pred(elem) == v:
                return elem
        return None

    converted = [
        (attr_get(attr.replace("__", ".")), value) for attr, value in attrs.items()
    ]

    for elem in iterable:
        if _all(pred(elem) == value for pred, value in converted):
            return elem
    return None


def find_and_get_lambda(iterable: dict, check: Callable[[Any], Any]) -> Optional[T]:
    for elem in iterable:
        if bool(check(elem)):
            return elem
    return None
