
import argparse
import logging
import time

from config import Config
from logger_config import setup_logger
from extract import collect_matches, get_items_json
from transform import build_dataframes
from load import save_all_to_csv, save_all_to_postgres  


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--players", type=int, default=5)
    parser.add_argument("--matches", type=int, default=2)
    parser.add_argument("--save-csv", choices=["yes","no"], default="yes")
    parser.add_argument("--save-db", choices=["yes","no"], default="yes")

    return parser.parse_args()

def main():
    start = time.time()
    setup_logger()

    args = get_args()
    config = Config()

    logging.info("EXTRACT started")

    matches = collect_matches(
        config=config,
        players_count=args.players,
        matches_per_player=args.matches
    )

    items_json = get_items_json(config)

    logging.info("Matches loaded: %s", len(matches))

    logging.info("TRANSFORM started")
    tables = build_dataframes(matches,items_json)

    logging.info("Players: %s", len(tables["players"]))
    logging.info("Matches: %s", len(tables["matches"]))
    logging.info("Participants: %s", len(tables["participants"]))
    logging.info("Items: %s", len(tables["items"]))


    logging.info("LOAD started")

    if args.save_csv == "yes":
        save_all_to_csv(tables, config.output_dir)

    if args.save_db == "yes":
        save_all_to_postgres(tables, config.db_config)  

    logging.info("Finished in %.2f sec", time.time() - start)

if __name__ == "__main__":
    main()
