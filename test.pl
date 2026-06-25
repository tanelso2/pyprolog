person(alice).
person(bob).
person(carol).
person(dan).
parent(alice, bob).
parent(alice, carol).
parent(bob, dan).
:- use_module(library(lists)).
sibling(X, Y) :- parent(P, X), parent(P, Y), X \= Y.
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).