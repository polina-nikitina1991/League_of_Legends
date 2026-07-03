--смотрим таблицу items
select * from items i limit 5;
-- смотрим таблицу matches
select * from matches limit 5;
-- смотрим таблицу matches_items
select * from matches_items limit 5;
-- смотрим таблицу participants
select * from participants limit 5;
-- смотрим таблицу players
select * from players limit 5;

--меняем значение duration в минуты сейчас указано в секундах
select *, ROUND((game_duration / 60.0),2) AS game_duration_min
from matches
limit 5;

-- смотрим Winrate по игрокам
SELECT 
    champion,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY champion
HAVING COUNT(*) > 2
ORDER BY winrate DESC; -- выборка не большая количесво максимальных побед 3

--KDA по чемпионам
SELECT 
    champion,
    ROUND(AVG((kills + assists) / NULLIF(deaths, 0)), 2) AS avg_kda
FROM participants
GROUP BY champion
ORDER BY avg_kda DESC;


--Эффективность экономики (золото → урон)
SELECT 
    champion,
    ROUND(AVG(damage / NULLIF(gold_earned, 0)), 4) AS dmg_per_gold
FROM participants
GROUP BY champion
ORDER BY dmg_per_gold DESC;

-- Vision vs Winrate
SELECT 
    CASE 
        WHEN vision_score < 10 THEN 'low'
        WHEN vision_score < 30 THEN 'medium'
        ELSE 'high'
    END AS vision_group,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY vision_group;

--Влияние объектов на победу
SELECT 
    ROUND(AVG(win::int) FILTER (WHERE dragon_kills > 0), 3) AS win_with_dragon,
    ROUND(AVG(win::int) FILTER (WHERE dragon_kills = 0), 3) AS win_without_dragon
FROM participants;

-- Лучшие позиции (roles)
SELECT 
    position,
    COUNT(*) AS games,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY position
ORDER BY winrate DESC;

-- Winrate предметов
SELECT 
    mi.item_id,
    COUNT(*) AS games,
    ROUND(AVG(p.win::int), 3) AS winrate
FROM matches_items mi
JOIN participants p 
    ON mi.match_id = p.match_id 
   AND mi.puuid = p.puuid
GROUP BY mi.item_id
HAVING COUNT(*) > 30

--Лучшие предметы для конкретного чемпиона
SELECT 
    p.champion,
    mi.item_id,
    COUNT(*) AS games,
    ROUND(AVG(p.win::int), 3) AS winrate
FROM matches_items mi
JOIN participants p 
    ON mi.match_id = p.match_id 
   AND mi.puuid = p.puuid
WHERE p.champion = 'Ahri'
GROUP BY p.champion, mi.item_id
HAVING COUNT(*) > 1
ORDER BY winrate DESC;

-- Влияние фарма (CS) на победу
SELECT 
    ROUND(AVG(win::int) FILTER (WHERE cs > 200), 3) AS win_high_cs,
    ROUND(AVG(win::int) FILTER (WHERE cs <= 200), 3) AS win_low_cs
FROM participants;
ORDER BY winrate DESC;

-- Урон vs победа
SELECT 
    CASE 
        WHEN damage < 10000 THEN 'low'
        WHEN damage < 20000 THEN 'medium'
        ELSE 'high'
    END AS dmg_group,
    ROUND(AVG(win::int), 3) AS winrate
FROM participants
GROUP BY dmg_group;

-- 
