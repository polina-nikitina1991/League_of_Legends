
import time
import logging
import requests
import json

def riot_get(url: str, api_key: str):

    """
    Отправляет GET‑запрос к API Riot Games с обработкой ограничения частоты запросов (rate limiting).

    При получении ответа с кодом 429 (Too Many Requests) функция ожидает указанное сервером время
    (из заголовка 'Retry-After') и повторяет запрос. Между успешными запросами делается пауза60
    в 0.06 секунды для соблюдения лимитов API.

    Args:
        url (str): URL‑адрес эндпоинта API Riot Games, к которому выполняется запрос.

    Returns:
        Dict[str, Any]: JSON‑ответ от API в виде словаря Python.

    Raises:
        requests.exceptions.HTTPError: Если запрос завершился с HTTP‑ошибкой,
            отличной от 429 (например, 404, 500 и т. д.).
        ValueError: Если значение в заголовке 'Retry-After' не может быть преобразовано в целое число.
        requests.exceptions.RequestException: При других ошибках запросов (сетевые проблемы и т. п.).

    Example:
        >>> response_data = riot_get("https://api.riotgames.com/lol/summoner/v4/summoners/by-name/ExampleName")
        >>> print(response_data["name"])
        ExampleName
    """

    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))
        logging.warning(f"Rate limit. Sleep {retry_after}s")
        time.sleep(retry_after)
        return riot_get(url, api_key)

    response.raise_for_status()
    time.sleep(0.06)
    return response.json()

def get_challenger_players(config, queue="RANKED_SOLO_5x5"):

    """
    Получает список игроков из Challenger-лиги по указанной очереди.

    Args:
        config: объект конфигурации (содержит region и api_key)
        queue (str): тип очереди (по умолчанию RANKED_SOLO_5x5)

    Returns:
        list[dict]: список игроков с данными (puuid, leaguePoints и др.)

    Используется как первый шаг пайплайна — источник топ-игроков.
    """    

    url = f"https://{config.region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}"
    return riot_get(url, config.api_key)["entries"]

def get_match_ids(config, puuid, count=20):

    """
    Получает список match_id для конкретного игрока по puuid.

    Args:
        config: объект конфигурации (routing_region, api_key)
        puuid (str): уникальный идентификатор игрока
        count (int): количество матчей для загрузки

    Returns:
        list[str]: список match_id

    Используется для получения матчей конкретного игрока.
    """

    url = f"https://{config.routing_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    return riot_get(url, config.api_key)

def get_match(config, match_id):

    """
    Загружает детальную информацию о конкретном матче.

    Args:
        config: объект конфигурации (routing_region, api_key)
        match_id (str): идентификатор матча

    Returns:
        dict: JSON с полной информацией о матче (metadata + info)

    Используется для последующей трансформации данных.
    """

    url = f"https://{config.routing_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    return riot_get(url, config.api_key)

def collect_players(config, players_count):

    """
    Отбирает топ-N игроков из Challenger-лиги по количеству LP.

    Args:
        config: объект конфигурации
        players_count (int): количество игроков для отбора

    Returns:
        list[dict]: отсортированный список игроков

    Логика:
        1. Получает всех challenger-игроков
        2. Сортирует по leaguePoints
        3. Берет топ-N

    Используется для ограничения объема данных.
    """

    players = get_challenger_players(config)
    return sorted(players, key=lambda x: x["leaguePoints"], reverse=True)[:players_count]

def collect_match_ids(config, players_count, matches_per_player):

    """
    Собирает уникальные match_id для выбранных игроков.

    Args:
        config: объект конфигурации
        players_count (int): количество игроков
        matches_per_player (int): количество матчей на игрока

    Returns:
        list[str]: уникальный список match_id

    Логика:
        1. Берет топ игроков
        2. Для каждого получает список матчей
        3. Объединяет и удаляет дубликаты

    Используется как промежуточный шаг перед загрузкой матчей.
    """

    ids = []
    for player in collect_players(config, players_count):
        try:
            ids.extend(get_match_ids(config, player["puuid"], matches_per_player))
        except Exception as e:
            logging.exception(e)
    return list(set(ids))

def collect_matches(config, players_count, matches_per_player):

    """
    Загружает полные данные матчей по выбранным игрокам.

    Args:
        config: объект конфигурации
        players_count (int): количество игроков
        matches_per_player (int): матчей на игрока

    Returns:
        list[dict]: список JSON матчей

    Логика:
        1. Получает список match_id
        2. Загружает каждый матч через API
        3. Собирает все матчи в список

    Это основной extract-этап ETL.
    """

    matches = []
    ids = collect_match_ids(config, players_count, matches_per_player)

    for match_id in ids:
        try:
            match = get_match(config, match_id)   
            match["region"] = config.region       
            matches.append(match)   

        except Exception as e:
            logging.exception(e)

    return matches

def get_items_dict(config):

    """
    Загружает актуальный справочник предметов с Data Dragon API.

    Args:
        config: объект конфигурации (не используется напрямую, но для консистентности)

    Returns:
        dict: словарь предметов (item_id → данные предмета)

    Логика:
        1. Получает список версий игры
        2. Берет последнюю версию
        3. Загружает JSON предметов

    Используется как справочник (dimension table).
    """

    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    versions = requests.get(url).json()
    latest = versions[0]

    item_url = f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/item.json"
    return requests.get(item_url).json()["data"]


def get_items_json(config):

    """
    Загружает локальный JSON-файл с данными предметов.

    Args:
        config: объект конфигурации (должен содержать items_path)

    Returns:
        dict: JSON с предметами

    Raises:
        Exception: если файл не найден или поврежден

    Используется как альтернатива API (например, для оффлайн-режима).
    """

    try:
        with open(config.items_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logging.info("Items JSON loaded")
            return data
    except Exception as e:
        logging.exception("Failed to load items JSON")
        raise e
