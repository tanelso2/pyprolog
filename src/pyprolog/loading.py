import logging
import tempfile

import janus_swi as janus

logger = logging.getLogger(__name__)


def bulk_load(facts: list[str]):
    prolog_content = "\n".join(facts)
    janus.consult("tmp", data=prolog_content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    facts = []
    for p in ["alice", "bob", "carol", "dan"]:
        facts.append(f"person({p}).")
    facts.append("parent(alice, bob).")
    facts.append("parent(alice, carol).")
    facts.append("parent(bob, dan).")
    facts.append(":- use_module(library(lists)).")
    facts.append("sibling(X, Y) :- parent(P, X), parent(P, Y), X \\= Y.")
    facts.append("grandparent(X, Z) :- parent(X, Y), parent(Y, Z).")
    bulk_load(facts)
    logging.info("Grandparents of Alice:")
    for r in janus.query("grandparent(alice, Gparent)"):
        logging.info(r["Gparent"])
    logging.info("Siblings of Alice:")
    for r in janus.query("sibling(alice, Sib)"):
        logging.info(r["Sib"])
