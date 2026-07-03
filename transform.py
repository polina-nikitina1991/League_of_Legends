
import pandas as pd

def transform_players(matches):
    rows = []
    for match in matches:
        for p in match["info"]["participants"]:
            rows.append({"puuid": p["puuid"]})
    return pd.DataFrame(rows).drop_duplicates()

def transform_matches(matches):
    rows = []
    for match in matches:
        info = match["info"]
        rows.append({
            "match_id": match["metadata"]["matchId"],
            "game_mode": info.get("gameMode"),
            "game_version": info.get("gameVersion"),
            "game_duration": info.get("gameDuration"),
            "game_start_ts": info.get("gameStartTimestamp")
        })
    return pd.DataFrame(rows).drop_duplicates(subset="match_id")

def transform_participants(matches):
    rows = []
    for match in matches:
        match_id = match["metadata"]["matchId"]
        for p in match["info"]["participants"]:
            rows.append({
                "match_id": match_id,
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
                        "puuid": puuid,
                        "item_id": item_id,
                        "slot": i
                    })

    return pd.DataFrame(rows)

def transform_items_dict(items_json):
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
    return {
        "players": transform_players(matches),
        "matches": transform_matches(matches),
        "participants": transform_participants(matches),
        "matches_items":transform_items(matches),
        "items":transform_items_dict(items_json)
    }
