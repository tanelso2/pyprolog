import logging
from typing import Iterable

from pyprolog.importers.mtg.facts import card_facts
from pyprolog.importers.mtg.scryfall import get_card_data
from pyprolog.prolog.engine import JanusEngine
from pyprolog.prolog.syntax import QueryConversion, convert_query, to_prolog_value

logger = logging.getLogger(__name__)


class MTGEngine(JanusEngine):
    def __init__(self) -> None:
        super().__init__()

    def load_all(self):
        logger.info("Loading cards from file on disk")
        cards = get_card_data()
        logger.info("Generating card facts")
        all_facts = card_facts(cards)
        logger.info("Add facts to Prolog engine")
        self.add_facts(all_facts)

    def _query_card_name_from_set_num_query(
        self, query: str, original_query_var: str = "X"
    ) -> QueryConversion:
        new_query_var = "Name"
        additional_rules = [
            f"card(_, {new_query_var}, {original_query_var}, _, _)",
        ]
        return convert_query(query, original_query_var, new_query_var, additional_rules)

    def query_color(self, color: str) -> Iterable[str]:
        safe_arg = to_prolog_value(color)
        query = f"card_color(X, {safe_arg})"
        qc = self._query_card_name_from_set_num_query(query)
        return self.query_converted(qc)


if __name__ == "__main__":
    LOG_FORMAT = (
        "%(asctime)s|%(levelname)s|%(name)s::%(funcName)s:%(lineno)d|%(message)s"
    )
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=None)
    eng = MTGEngine()
    eng.load_all()

    logger.info("Querying engine")
    COLORS = [
        ("Black", "B"),
        ("Blue", "U"),
        ("Green", "G"),
        ("Red", "R"),
        ("White", "W"),
    ]
    for color, abbr in COLORS:
        results = list(eng.query_color(abbr))
        logger.info(f"Found {len(results)} {color} cards")
