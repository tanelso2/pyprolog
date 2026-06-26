import logging

from pyprolog.importers.mtg.scryfall import Card, get_card_data
from pyprolog.prolog.facts import GeneratedPrologFact, PrologFact, all_to_prolog
from pyprolog.prolog.engine import JanusEngine

logger = logging.getLogger(__name__)


class CardFact(GeneratedPrologFact):
    id: str
    name: str
    set_num: str
    set_code: str
    collector_number: str

    def __init__(self, card: Card):
        self.id = card.id
        self.name = card.name
        self.set_num = card.set_num
        self.set_code = card.set
        self.collector_number = card.collector_number
        super().__init__(
            constructor="card",
            args=[
                self.id,
                self.name,
                self.set_num,
                self.set_code,
                self.collector_number,
            ],
        )


class CardRarity(GeneratedPrologFact):
    set_num: str
    rarity: str

    def __init__(self, card: Card):
        self.set_num = card.set_num
        self.rarity = card.rarity
        super().__init__(constructor="card_rarity", args=[self.set_num, self.rarity])


class CardColor(GeneratedPrologFact):
    set_num: str
    color: str

    def __init__(self, card: Card, color: str):
        self.set_num = card.set_num
        self.color = color
        super().__init__(constructor="card_color", args=[self.set_num, self.color])


class CardColorIdentity(GeneratedPrologFact):
    set_num: str
    color: str

    def __init__(self, card: Card, color: str):
        self.set_num = card.set_num
        self.color = color
        super().__init__(
            constructor="card_color_identity", args=[self.set_num, self.color]
        )


class CardLegality(GeneratedPrologFact):
    set_num: str
    mode: str
    legality: str

    def __init__(self, card: Card, mode: str, legality: str):
        self.set_num = card.set_num
        self.mode = mode
        self.legality = legality
        super().__init__(
            constructor="card_legality",
            args=[
                self.set_num,
                self.mode,
                self.legality,
            ],
        )


def generate_card_facts(card: Card) -> list[PrologFact]:
    ret = []
    ret.append(CardFact(card))
    ret.append(CardRarity(card))
    if card.colors is not None:
        for c in card.colors:
            ret.append(CardColor(card, c))
    for c in card.color_identity:
        ret.append(CardColorIdentity(card, c))
    for format, legality in card.legalities.items():
        ret.append(CardLegality(card, format, legality))

    return ret


def card_facts(cards: list[Card]) -> list[PrologFact]:
    ret = []
    for c in cards:
        ret.extend(generate_card_facts(c))
    return ret


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logger.info("Loading cards")
    cards = get_card_data()

    logger.info("Generating facts from cards")
    all_facts = card_facts(cards)

    logger.info("Adding facts to prolog engine")
    prolog = JanusEngine()
    prolog.add_facts(all_facts)

    logger.info("Querying prolog engine")
    results = list(prolog.query_binary_relation("card_color", "B", arg_position="last"))
    print(f"Found {len(results)} Black cards")
    results = list(prolog.query_binary_relation("card_color", "U", arg_position="last"))
    print(f"Found {len(results)} Blue cards")
    results = list(prolog.query_binary_relation("card_color", "G", arg_position="last"))
    print(f"Found {len(results)} Green cards")
    results = list(prolog.query_binary_relation("card_color", "R", arg_position="last"))
    print(f"Found {len(results)} Red cards")
    results = list(prolog.query_binary_relation("card_color", "W", arg_position="last"))
    print(f"Found {len(results)} White cards")
