
from pathlib import Path
import logging
from sqlalchemy import create_engine


def save_all_to_csv(tables, output_dir):

    """
    Сохраняет все таблицы в CSV файлы.

    Каждая таблица из словаря сохраняется в отдельный файл
    с именем таблицы (например: players.csv, matches.csv).

    Параметры:
        tables — словарь {имя_таблицы: DataFrame}
        output_dir — путь к папке для сохранения файлов

    Что делает:
        - создаёт папку, если её нет
        - сохраняет каждый DataFrame в CSV
        - логирует путь сохранённого файла

    Используется для:
        - локального хранения данных
        - дебага и проверки данных
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, df in tables.items():
        path = out / f"{name}.csv"
        df.to_csv(path, index=False)
        logging.info(f"CSV saved: {path}")


def save_all_to_postgres(tables, db_config):

    """
    Сохраняет все таблицы в базу данных PostgreSQL.

    Подключается к базе и записывает каждую таблицу
    из словаря как отдельную таблицу в БД.

    Параметры:
        tables — словарь {имя_таблицы: DataFrame}
        db_config — настройки подключения:
            user, password, host, port, database

    Что делает:
        - создаёт подключение к PostgreSQL
        - записывает таблицы через pandas.to_sql()
        - перезаписывает таблицы (if_exists="replace")
        - логирует успешную загрузку

    Ошибки:
        - при проблемах с подключением или записью
          логирует ошибку и пробрасывает исключение

    Используется как финальный шаг ETL (load слой).
    """

    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

    engine = create_engine(connection_string)

    try:
        with engine.begin() as conn:
            for name, df in tables.items():
                df.to_sql(name, conn, if_exists="append", index=False)
                logging.info(f"Table saved: {name}")
    except Exception as e:
        logging.exception("Error while saving to Postgres")
        raise e
