import pytest

from pyprolog.prolog.engine import JanusEngine, PrologEngine
from pyprolog.prolog.facts import PrologFact, GeneratedPrologFact, RawPrologFact


@pytest.fixture
def prolog() -> PrologEngine:
    return JanusEngine()


_USE_LIST_MODULE_FACT = RawPrologFact(":- use_module(library(lists)).")
_SIBLING_FACT_STR = "sibling(X, Y) :- parent(P, X), parent(P,Y), X \\= Y."
_SIBLING_FACT = RawPrologFact(_SIBLING_FACT_STR)


class Person(GeneratedPrologFact):
    name: str

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(constructor="person", args=[self.name])


class ParentChildRelationship(GeneratedPrologFact):
    parent: Person
    child: Person

    def __init__(self, parent: Person, child: Person) -> None:
        self.parent = parent
        self.child = child
        super().__init__(constructor="parent", args=[parent.name, child.name])


def query_persons(prolog: PrologEngine) -> list[str]:
    return list(prolog.query_monary_relation("person"))


def query_children(prolog: PrologEngine, parent: Person) -> list[str]:
    return list(prolog.query_binary_relation("parent", parent.name))


def query_parents(prolog: PrologEngine, child: Person) -> list[str]:
    return list(prolog.query_binary_relation("parent", child.name, arg_position="last"))


def query_siblings(prolog: PrologEngine, x: Person) -> list[str]:
    return list(prolog.query_binary_relation("sibling", x.name))


def test_children(prolog: PrologEngine):
    anna = Person("Anna")
    elsa = Person("Elsa")
    king = Person("The King")
    anna_parent = ParentChildRelationship(parent=king, child=anna)
    elsa_parent = ParentChildRelationship(parent=king, child=elsa)
    facts = [
        _USE_LIST_MODULE_FACT,
        _SIBLING_FACT,
        anna,
        elsa,
        king,
        anna_parent,
        elsa_parent,
    ]
    prolog.add_facts(facts)

    results = query_persons(prolog)
    assert len(results) == 3
    assert "Elsa" in results
    assert "The King" in results
    assert "Anna" in results

    results = query_parents(prolog, king)
    assert len(results) == 0

    results = query_parents(prolog, anna)
    assert len(results) == 1
    assert results[0] == "The King"

    results = query_parents(prolog, elsa)
    assert len(results) == 1

    results = query_siblings(prolog, king)
    assert len(results) == 0

    results = query_siblings(prolog, anna)
    assert len(results) == 1
    assert results[0] == "Elsa"

    results = query_children(prolog, king)
    assert len(results) == 2
    assert "Elsa" in results
    assert "Anna" in results
