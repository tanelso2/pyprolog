import logging
from typing import Generator, Literal

import janus_swi as janus

logger = logging.getLogger(__name__)


def _yield_variable(query: str, variable_name: str) -> Generator[str, None, None]:
    for r in janus.query(query):
        yield r[variable_name]


def query_for_variable(query: str, variable_name: str) -> list[str]:
    assert variable_name in query
    return list(_yield_variable(query, variable_name))


def query_binary_relation(
    relation: str, arg: str, arg_postion: Literal["first", "last"] = "first"
) -> list[str]:
    query = (
        f"{relation}({arg}, X)" if arg_postion == "first" else f"{relation}(X, {arg})"
    )
    return query_for_variable(query, variable_name="X")
