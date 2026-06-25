from pathlib import Path
from typing import Any, Iterable, Literal, Protocol, override

import janus_swi as janus

from pyprolog.prolog.facts import PrologFact, all_to_prolog
from pyprolog.prolog.syntax import (
    is_valid_predicate_name,
    is_valid_variable_name,
    to_prolog_value,
)


class PrologEngine(Protocol):
    def add_facts(self, facts: Iterable[PrologFact]) -> None: ...

    def load_facts_file(self, path: Path) -> None: ...

    def query(self, query: str) -> Iterable[dict[str, str]]: ...

    def query_for_variable(self, query: str, var: str) -> Iterable[str]:
        if var not in query:
            raise ValueError(
                f"Cannot query for var '{var}' when it is not present in query '{query}'"
            )
        if not is_valid_variable_name(var):
            raise ValueError(f"{var} is not a valid Prolog variable identifier")
        return [x[var] for x in self.query(query)]

    def query_monary_relation(self, relation: str) -> Iterable[str]:
        if not is_valid_predicate_name(relation):
            raise ValueError(f"{relation} is not a valid Prolog predicate identifier")
        var = "X"
        query = f"{relation}({var})"
        return self.query_for_variable(query, var)

    def query_binary_relation(
        self, relation: str, arg: Any, arg_position: Literal["first", "last"] = "first"
    ) -> Iterable[str]:
        if not is_valid_predicate_name(relation):
            raise ValueError(f"{relation} is not a valid Prolog predicate identifier")
        var = "X"
        safe_arg = to_prolog_value(arg)
        match arg_position:
            case "first":
                query = f"{relation}({safe_arg}, {var})"
            case "last":
                query = f"{relation}({var}, {safe_arg})"
        return self.query_for_variable(query, var)


class JanusEngine(PrologEngine):
    @override
    def query(self, query: str) -> Iterable[dict[str, str]]:
        for x in janus.query(query):
            yield x

    @override
    def add_facts(self, facts: Iterable[PrologFact]) -> None:
        content = all_to_prolog(facts)
        janus.consult("tmp", data=content)

    @override
    def load_facts_file(self, path: Path) -> None:
        content = path.read_text()
        janus.consult("tmp", data=content)
