from abc import abstractmethod
from dataclasses import dataclass
import logging
from typing import Iterable, override

import janus_swi as janus

from pyprolog.prolog.syntax import (
    KnownConversions,
    is_valid_predicate_name,
    to_prolog_value,
)

logger = logging.getLogger(__name__)


class PrologFact:
    @abstractmethod
    def to_prolog(self) -> str: ...


@dataclass
class RawPrologFact(PrologFact):
    raw: str

    @override
    def to_prolog(self) -> str:
        return self.raw


class GeneratedPrologFact(PrologFact):
    constructor: str
    _raw_args: list[KnownConversions]
    args: list[str]

    def __init__(self, constructor: str, args: list[KnownConversions]) -> None:
        assert is_valid_predicate_name(constructor)
        self.constructor = constructor
        self._raw_args = args
        self.args = [to_prolog_value(arg) for arg in args]

    @override
    def to_prolog(self) -> str:
        return f"{self.constructor}({', '.join(self.args)})."


def all_to_prolog(facts: Iterable[PrologFact]) -> str:
    fact_strs = sorted([x.to_prolog() for x in facts])
    for f in fact_strs:
        if not f.endswith("."):
            raise ValueError(
                f"{f} is not a valid Prolog fact - it does not end in a period."
            )
    ret = "\n".join(fact_strs)
    return ret
