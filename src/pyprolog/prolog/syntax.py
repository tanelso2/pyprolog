from dataclasses import dataclass
import math
import re
from typing import Any, Iterable

# Must start with lowercase letter, then can be alphanumeric with underscores
_VALID_PREDICATE = re.compile(r"^[a-z][A-Za-z0-9_]*$")

# Must start with uppercase letter or underscore, then can be alphanumeric with underscores
_VALID_VARIABLE = re.compile(r"^[A-Z_][A-Za-z0-9_]*$")


def is_valid_predicate_name(name: str) -> bool:
    return _VALID_PREDICATE.fullmatch(name) is not None


def is_valid_variable_name(name: str) -> bool:
    return _VALID_VARIABLE.fullmatch(name) is not None


_ATOM_ESCAPE_PAIRS: list[tuple[str, str]] = [
    ("\\", "\\\\"),
    ("'", "''"),
    ("\n", "\\n"),
    ("\r", "\\r"),
    ("\t", "\\t"),
]


def quote_atom(s: str) -> str:
    curr = s
    for old, new in _ATOM_ESCAPE_PAIRS:
        curr = curr.replace(old, new)
    return "'" + curr + "'"


type KnownConversions = None | bool | int | float | str


def to_prolog_value(value: Any) -> str:
    match value:
        case None:
            return "null"
        case bool() as b:
            return "true" if b else "false"
        case int() as i:
            return str(i)
        case float() as f:
            if math.isfinite(f):
                return repr(f)
            else:
                raise ValueError(f"Invalid float for Prolog: {f}")
        case str() as s:
            return quote_atom(s)
        case _:
            raise TypeError(
                f"Unknown conversion from type {type(value)!r} to Prolog value"
            )


@dataclass
class QueryConversion:
    new_query: str
    new_var: str


def convert_query(
    orig: str,
    orig_var: str,
    new_var: str,
    additional_rules: Iterable[str] = [],
) -> QueryConversion:
    assert is_valid_variable_name(orig_var)
    assert is_valid_variable_name(new_var)
    query = orig
    assert new_var not in query
    rules = list(additional_rules)
    rules.append(orig)
    new_query = ", ".join(rules)
    assert new_var in new_query
    return QueryConversion(new_query=new_query, new_var=new_var)
