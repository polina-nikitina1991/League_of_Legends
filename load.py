
from pathlib import Path
import logging
from sqlalchemy import create_engine


def save_all_to_csv(tables, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, df in tables.items():
        path = out / f"{name}.csv"
        df.to_csv(path, index=False)
        logging.info(f"CSV saved: {path}")


def save_all_to_postgres(tables, db_config):
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

    engine = create_engine(connection_string)

    try:
        with engine.begin() as conn:
            for name, df in tables.items():
                df.to_sql(name, conn, if_exists="replace", index=False)
                logging.info(f"Table saved: {name}")
    except Exception as e:
        logging.exception("Error while saving to Postgres")
        raise e
