from pathlib import Path
import tempfile
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, TypeAdapter
import requests

_SELECTED_BULK_DATA_TYPES = [
    "default_cards",
    "rulings",
    "art_tags",
    "oracle_tags",
]


class ScryfallApiResponse(BaseModel):
    object: str
    has_more: bool
    # data: list[dict[str, str]] = Field(frozen=True)


class BulkData(BaseModel):
    object: str
    id: str
    type: str
    download_uri: str

    model_config = ConfigDict(extra="allow")


class BulkDataResponse(ScryfallApiResponse, BaseModel):
    data: list[BulkData]


def current_bulk_data_locations() -> BulkDataResponse:
    url = "https://api.scryfall.com/bulk-data"
    headers = {
        "User-Agent": "MTGDataImporter/0.1",
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return BulkDataResponse.model_validate_json(resp.content)


def download_bulk_data_item(b: BulkData, p: Path):
    url = b.download_uri
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with p.open("wb") as f:
        for content in resp.iter_content(chunk_size=None):
            f.write(content)


def download_bulk_data(dir: Path):
    if not dir.is_dir():
        raise EnvironmentError(f"{dir} is not a directory")
    locs = current_bulk_data_locations()
    for b in locs.data:
        if b.type not in _SELECTED_BULK_DATA_TYPES:
            continue
        download_file = dir / f"{b.type}.json"
        download_bulk_data_item(b, download_file)


class Card(BaseModel):
    object: str
    id: str
    oracle_id: Optional[str] = None
    name: str
    lang: str
    released_at: str
    layout: str
    image_uris: Optional[dict[str, str]] = None
    mana_cost: Optional[str] = None
    cmc: Optional[float] = None
    type_line: Optional[str] = None
    oracle_text: Optional[str] = None
    colors: Optional[list[str]] = None
    color_identity: list[str]
    produced_mana: Optional[list[str]] = None
    keywords: list[str]
    legalities: dict[str, Literal["legal", "not_legal", "banned", "restricted"]]
    games: list[str]
    reserved: bool
    game_changer: bool
    foil: bool
    nonfoil: bool
    promo: bool
    reprint: bool
    variant: Optional[bool] = None
    set_id: str
    set: str
    set_name: str
    set_type: str
    collector_number: str
    digital: bool
    rarity: str
    artist: str
    full_art: bool
    textless: bool
    booster: bool

    model_config = ConfigDict(extra="allow")

    @property
    def set_num(self) -> str:
        return f"{self.set}-{self.collector_number}"


_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "pyprolog" / "scryfall"


def get_card_data(dir: Path = _DEFAULT_CACHE_DIR) -> list[Card]:
    default_cards_file = dir / "default_cards.json"
    if not default_cards_file.exists():
        raise EnvironmentError(f"{default_cards_file} does not exist")
    if not default_cards_file.is_file():
        raise EnvironmentError(f"{default_cards_file} is not a file.")
    return TypeAdapter(list[Card]).validate_json(default_cards_file.read_bytes())


if __name__ == "__main__":
    cache_dir = Path.home() / ".cache" / "pyprolog"
    scryfall_dir = cache_dir / "scryfall"
    scryfall_dir.mkdir(parents=True, exist_ok=True)
    cards = get_card_data(scryfall_dir)
    print(f"{len(cards)=}")
