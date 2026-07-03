-- смотрим таблицы
SELECT * FROM items LIMIT 5;
SELECT * FROM matches LIMIT 5;
SELECT * FROM matches_items LIMIT 5;
SELECT * FROM participants LIMIT 5;
SELECT * FROM players LIMIT 5;


-- длительность матча в минутах + регион
SELECT 
    region,
    match_id,
    ROUND(game_duration / 60.0, 2) AS game_duration_min
FROM matches
LIMIT 5;


-- Winrate по чемпионам с учетом региона
SELECT 
    region,
    champion,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY region, champion
HAVING COUNT(*) > 2
ORDER BY region, winrate DESC;


-- KDA по чемпионам
SELECT 
    region,
    champion,
    ROUND(AVG((kills + assists) / NULLIF(deaths, 0)), 2) AS avg_kda
FROM participants
GROUP BY region, champion
ORDER BY region, avg_kda DESC;


-- Экономика (урон на золото)
SELECT 
    region,
    champion,
    ROUND(AVG(damage / NULLIF(gold_earned, 0)), 4) AS dmg_per_gold
FROM participants
GROUP BY region, champion
ORDER BY region, dmg_per_gold DESC;


-- Vision vs Winrate
SELECT 
    region,
    CASE 
        WHEN vision_score < 10 THEN 'low'
        WHEN vision_score < 30 THEN 'medium'
        ELSE 'high'
    END AS vision_group,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY region, vision_group;


-- Влияние драконов
SELECT 
    region,
    ROUND(AVG(win::int) FILTER (WHERE dragon_kills > 0), 3) AS win_with_dragon,
    ROUND(AVG(win::int) FILTER (WHERE dragon_kills = 0), 3) AS win_without_dragon
FROM participants
GROUP BY region;


-- Позиции (roles)
SELECT 
    region,
    position,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
WHERE position IS NOT NULL
  AND position <> ''
GROUP BY region, position
ORDER BY region, winrate DESC;


-- Winrate предметов
SELECT 
    p.region,
    mi.item_id,
    COUNT(*) AS games,
    ROUND(AVG(p.win::int), 3) AS winrate
FROM matches_items mi
JOIN participants p 
    ON mi.match_id = p.match_id 
   AND mi.puuid = p.puuid
GROUP BY p.region, mi.item_id
HAVING COUNT(*) > 30
ORDER BY p.region, winrate DESC;


-- Предметы для чемпиона
SELECT 
    p.region,
    p.champion,
    mi.item_id,
    COUNT(*) AS games,
    ROUND(AVG(p.win::int), 3) AS winrate
FROM matches_items mi
JOIN participants p 
    ON mi.match_id = p.match_id 
   AND mi.puuid = p.puuid
WHERE p.champion = 'Ahri'
GROUP BY p.region, p.champion, mi.item_id
HAVING COUNT(*) > 1
ORDER BY p.region, winrate DESC;


-- CS влияние
SELECT 
    region,
    ROUND(AVG(win::int) FILTER (WHERE cs > 200), 3) AS win_high_cs,
    ROUND(AVG(win::int) FILTER (WHERE cs <= 200), 3) AS win_low_cs
FROM participants
GROUP BY region;


-- Урон vs победа
SELECT 
    region,
    CASE 
        WHEN damage < 10000 THEN 'low'
        WHEN damage < 20000 THEN 'medium'
        ELSE 'high'
    END AS dmg_group,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY region, dmg_group;

-- 
