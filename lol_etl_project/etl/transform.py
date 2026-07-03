
import pandas as pd

def transform_players(matches):

    """
    Формирует таблицу игроков (players).

    Извлекает уникальные puuid всех игроков из списка матчей.

    Параметры:
        matches — список JSON матчей (результат collect_matches)

    Возвращает:
        DataFrame с одним столбцом:
            puuid — уникальный идентификатор игрока

    Особенности:
        - удаляет дубликаты
        - используется как справочник игроков
    """

    rows = []
    for match in matches:
        for p in match["info"]["participants"]:
            rows.append({"puuid": p["puuid"]})
    return pd.DataFrame(rows).drop_duplicates()

def transform_matches(matches):

    """
    Формирует таблицу матчей (matches).

    Извлекает основную информацию о каждом матче.

    Параметры:
        matches — список JSON матчей

    Возвращает:
        DataFrame со столбцами:
            match_id — id матча
            game_mode — режим игры
            game_version — версия игры
            game_duration — длительность
            game_start_ts — время начала

    Особенности:
        - один матч = одна строка
        - удаляет дубликаты по match_id
    """

    rows = []
    for match in matches:
        info = match["info"]
        rows.append({
            "match_id": match["metadata"]["matchId"],
            "region": match.get("region"),
            "game_mode": info.get("gameMode"),
            "game_version": info.get("gameVersion"),
            "game_duration": info.get("gameDuration"),
            "game_start_ts": info.get("gameStartTimestamp")
        })
    return pd.DataFrame(rows).drop_duplicates(subset="match_id")

def transform_participants(matches):

    """
    Формирует таблицу игроков в матчах (participants).

    Каждая строка — это один игрок в одном матче.

    Параметры:
        matches — список JSON матчей

    Возвращает:
        DataFrame со столбцами:
            match_id — матч
            puuid — игрок
            champion — чемпион
            kills, deaths, assists — боевые показатели
            gold_earned, gold_spent — экономика
            damage, damage_taken — урон
            cs, jungle_cs — фарм
            vision_score, wards_* — вижен
            position — роль
            dragon_kills, baron_kills, turret_kills — объекты
            win — победа (0/1)

    Особенности:
        - основной факт (fact table)
        - используется для всей аналитики
    """

    rows = []
    for match in matches:
        match_id = match["metadata"]["matchId"]
        for p in match["info"]["participants"]:
            rows.append({
                "match_id": match_id,
                "region": match.get("region"),
                "puuid": p["puuid"],
                "champion": p["championName"],
                "kills": p["kills"],
                "deaths": p["deaths"],
                "assists": p["assists"],
                "gold_earned": p["goldEarned"],
                "total_damage_to_champions": p["totalDamageDealtToChampions"],
                "vision_score": p["visionScore"],
                "win": int(p["win"]),
                "gold_spent": p["goldSpent"],
                "damage": p["totalDamageDealtToChampions"],
                "damage_taken": p["totalDamageTaken"],
                "damage_to_objectives": p["damageDealtToObjectives"],
                "cs": p["totalMinionsKilled"],
                "jungle_cs": p["neutralMinionsKilled"],
                "wards_placed": p["wardsPlaced"],
                "wards_killed": p["wardsKilled"],
                "position": p["teamPosition"],
                "dragon_kills": p["dragonKills"],
                "baron_kills": p["baronKills"],
                "turret_kills": p["turretKills"]
            })
    return pd.DataFrame(rows)

def transform_items(matches):

    """
    Формирует таблицу предметов в матчах (match_items).

    Каждая строка — это один предмет у игрока в конкретном матче.

    Параметры:
        matches — список JSON матчей

    Возвращает:
        DataFrame со столбцами:
            match_id — матч
            puuid — игрок
            item_id — предмет
            slot — слот (0–6)

    Особенности:
        - пропускает пустые слоты (item_id = 0)
        - используется для анализа билдов
    """

    rows = []

    for match in matches:
        match_id = match["metadata"]["matchId"]

        for p in match["info"]["participants"]:
            puuid = p["puuid"]

            # 7 слотов предметов
            for i in range(7):
                item_id = p.get(f"item{i}")

                # пропускаем пустые (0)
                if item_id and item_id != 0:
                    rows.append({
                        "match_id": match_id,
                        "region": match.get("region"),
                        "puuid": puuid,
                        "item_id": item_id,
                        "slot": i
                    })

    return pd.DataFrame(rows)

def transform_items_dict(items_json):

    """
    Формирует справочник предметов (items).

    Преобразует JSON со всеми предметами в табличный вид.

    Параметры:
        items_json — JSON с предметами (из файла или API)

    Возвращает:
        DataFrame со столбцами:
            item_id — id предмета
            name — название
            price — стоимость
            sell_price — цена продажи

    Особенности:
        - dimension table (справочник)
        - используется для расшифровки item_id
    """

    rows = []

    for item_id, item in items_json["data"].items():
        rows.append({
            "item_id": int(item_id),
            "name": item.get("name"),
            "price": item.get("gold", {}).get("total"),
            "sell_price": item.get("gold", {}).get("sell")
        })

    return pd.DataFrame(rows)

def build_dataframes(matches,items_json):

    """
    Собирает все таблицы для загрузки (transform-слой).

    Объединяет результаты всех transform-функций
    в единый словарь датафреймов.

    Параметры:
        matches — список матчей
        items_json — JSON со справочником предметов

    Возвращает:
        dict:
            players — таблица игроков
            matches — таблица матчей
            participants — таблица игроков в матчах
            matches_items — предметы игроков
            items — справочник предметов

    Особенности:
        - финальный шаг transform перед загрузкой (load)
    """

    return {
        "players": transform_players(matches),
        "matches": transform_matches(matches),
        "participants": transform_participants(matches),
        "matches_items":transform_items(matches),
        "items":transform_items_dict(items_json)
    }
