import janus_swi as janus

from pyprolog.prolog.facts import (
    GeneratedPrologFact,
    RawPrologFact,
    bulk_load,
    PrologFact,
)
from pyprolog.prolog.query import query_binary_relation, query_for_variable


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


def query_siblings(p: Person) -> list[str]:
    return query_binary_relation("sibling", p.name)


def test_to_prolog():
    ann = Person("ann")
    assert ann.to_prolog() == "person(ann)."
    carol = Person("carol")
    assert carol.to_prolog() == "person(carol)."
    agnes = Person("agnes")
    assert agnes.to_prolog() == "person(agnes)."
    parent_aa = ParentChildRelationship(parent=agnes, child=ann)
    parent_ac = ParentChildRelationship(parent=agnes, child=carol)
    assert parent_aa.to_prolog() == "parent(agnes, ann)."
    assert parent_ac.to_prolog() == "parent(agnes, carol)."
    sibling_def_str = "sibling(X, Y) :- parent(P, X), parent(P,Y), X \\= Y."
    sibling_def = RawPrologFact(sibling_def_str)
    assert sibling_def_str == sibling_def.to_prolog()


def test_generating_and_querying_prolog():
    use_module_list_def = RawPrologFact(":- use_module(library(lists)).")
    ann = Person("ann")
    carol = Person("carol")
    agnes = Person("agnes")
    parent_aa = ParentChildRelationship(parent=agnes, child=ann)
    parent_ac = ParentChildRelationship(parent=agnes, child=carol)
    sibling_def_str = "sibling(X, Y) :- parent(P, X), parent(P,Y), X \\= Y."
    sibling_def = RawPrologFact(sibling_def_str)
    facts: list[PrologFact] = [
        use_module_list_def,
        ann,
        carol,
        agnes,
        parent_aa,
        parent_ac,
        sibling_def,
    ]
    bulk_load(facts)
    results = list(janus.query("sibling(ann, Sib)"))
    assert len(results) == 1
    assert results[0]["Sib"] == "carol"
    results = list(janus.query("sibling(agnes, Sib)"))
    assert len(results) == 0
    results = query_for_variable("sibling(agnes, Sib)", "Sib")
    assert len(results) == 0
    results = query_for_variable("sibling(carol, Sib)", "Sib")
    assert len(results) == 1
    assert results[0] == "ann"

    results = query_siblings(ann)
    assert len(results) == 1
    assert results[0] == "carol"
