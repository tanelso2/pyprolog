import janus_swi as janus

from pyprolog.prolog.facts import (
    GeneratedPrologFact,
    RawPrologFact,
    PrologFact,
)


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


_SIBLING_FACT_STR = "sibling(X, Y) :- parent(P, X), parent(P,Y), X \\= Y."
_SIBLING_FACT = RawPrologFact(_SIBLING_FACT_STR)


def test_to_prolog_generated_facts():
    anna = Person("anna")
    assert anna.to_prolog() == "person('anna')."
    elsa = Person("Elsa")
    assert elsa.to_prolog() == "person('Elsa')."
    king = Person("The King")
    assert king.to_prolog() == "person('The King')."
    parent_aa = ParentChildRelationship(parent=king, child=anna)
    parent_ae = ParentChildRelationship(parent=king, child=elsa)
    assert parent_aa.to_prolog() == "parent('The King', 'anna')."
    assert parent_ae.to_prolog() == "parent('The King', 'Elsa')."


def test_to_prolog_raw_fact():
    assert _SIBLING_FACT_STR == _SIBLING_FACT.to_prolog()
