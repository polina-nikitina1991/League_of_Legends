
from dataclasses import dataclass

@dataclass
class Config:
    api_key: str = "RGAPI-ccf9acdd-8cb4-454f-a846-c2d4557cdcbc"
    region: str = "euw1"
    routing_region: str = "europe"

    players_count: int = 60
    matches_per_player: int = 40

    save_csv: bool = True
    save_db: bool = True

    output_dir: str = "lol_output"

    db_config: dict = None

    def __post_init__(self):
        self.db_config = {
            "user": "postgres",
            "password": "89517088162Baba8609",
            "host": "localhost",
            "port": "5432",
            "database": "L_L_db"
        }

    items_path: str = r"C:\Users\allul\OneDrive\Desktop\учеба\самостоятельная учеба\проект мастерская\raw\raw\static\items.json"
