from abc import abstractmethod
from dataclasses import dataclass
import logging
from typing import Iterable, override

import janus_swi as janus

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


@dataclass
class GeneratedPrologFact(PrologFact):
    constructor: str
    args: list[str]

    @override
    def to_prolog(self) -> str:
        return f"{self.constructor}({', '.join(self.args)})."


def all_to_prolog(facts: Iterable[PrologFact]) -> str:
    fact_strs = [x.to_prolog() for x in facts]
    ret = "\n".join(fact_strs)
    return ret


def bulk_load(facts: Iterable[PrologFact]):
    content = all_to_prolog(facts)
    janus.consult("tmp", data=content)
