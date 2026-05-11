-- =============================================================================
-- posts_view: Нормализованное основное представление с производными полями.
-- Присоединяет число подписчиков на момент posted_at из groups_raw.
-- =============================================================================
CREATE OR REPLACE VIEW posts_view AS
SELECT
    p.id,
    p.group_id,
    p.post_id,
    p.posted_at,
    p.posted_at::date                                AS post_date,
    EXTRACT(ISODOW FROM p.posted_at)::int           AS day_of_week,    -- 1=пн, 7=вс
    EXTRACT(HOUR FROM p.posted_at)::int             AS hour_of_day,
    p.content_type,
    p.likes_count,
    p.comments_count,
    p.reposts_count,
    p.views_count,
    (p.likes_count + p.comments_count + p.reposts_count) AS reactions_total,
    -- последний снапшот подписчиков НА дату публикации
    (SELECT g.members_count
       FROM groups_raw g
      WHERE g.group_id = p.group_id
        AND g.snapshot_at <= p.posted_at
      ORDER BY g.snapshot_at DESC
      LIMIT 1)                                       AS members_at_post,
    p.text,
    p.fetched_at
FROM posts_raw p;


-- =============================================================================
-- Агрегационные функции (table-valued functions) для дашборда.
-- Период задаётся параметрами p_date_from / p_date_to.
-- =============================================================================

-- agg_absolute: Абсолютные показатели за период (формулы 1.1 подготовка).
CREATE OR REPLACE FUNCTION agg_absolute(p_date_from date, p_date_to date)
RETURNS TABLE (
    total_views     bigint,
    total_likes     bigint,
    total_comments  bigint,
    total_reposts   bigint,
    total_reactions bigint,
    posts_count     bigint
) LANGUAGE sql STABLE AS $$
    SELECT
        COALESCE(SUM(views_count), 0)::bigint,
        COALESCE(SUM(likes_count), 0)::bigint,
        COALESCE(SUM(comments_count), 0)::bigint,
        COALESCE(SUM(reposts_count), 0)::bigint,
        COALESCE(SUM(reactions_total), 0)::bigint,
        COUNT(*)::bigint
    FROM posts_view
    WHERE post_date BETWEEN p_date_from AND p_date_to;
$$;


-- agg_engagement: Коэффициенты вовлечённости (формулы 1.2–1.6).
-- ERpost_avg  = ΣR / (N × n) × 100  (формула 1.2)
-- ERview_avg  = среднее по постам ERview_i = R_i/V_i × 100  (формула 1.4)
-- ERday_avg   = ΣR_day / (d × n) × 100 — считается через подзапрос по дням  (формула 1.6)
CREATE OR REPLACE FUNCTION agg_engagement(p_date_from date, p_date_to date)
RETURNS TABLE (
    er_post_avg     numeric,
    er_view_avg     numeric,
    er_day_avg      numeric,
    members_current bigint
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (
      SELECT members_count
        FROM groups_raw
       ORDER BY snapshot_at DESC
       LIMIT 1
  ),
  posts AS (
      SELECT reactions_total, views_count
        FROM posts_view
       WHERE post_date BETWEEN p_date_from AND p_date_to
  ),
  day_reactions AS (
      SELECT SUM(reactions_total) AS r_day
        FROM posts_view
       WHERE post_date BETWEEN p_date_from AND p_date_to
       GROUP BY post_date
  )
SELECT
    -- ERpost_avg: ΣR / (N × n) × 100
    CASE WHEN COUNT(p.*) = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(SUM(p.reactions_total)::numeric / (COUNT(p.*) * lm.members_count) * 100, 4)
    END,
    -- ERview_avg: среднее ERview_i по постам с просмотрами > 0
    CASE WHEN COUNT(*) FILTER (WHERE p.views_count > 0) = 0
         THEN NULL
         ELSE ROUND(
             AVG(CASE WHEN p.views_count > 0
                      THEN p.reactions_total::numeric / p.views_count * 100
                 END), 4)
    END,
    -- ERday_avg: среднее ERday по дням
    CASE WHEN (SELECT COUNT(*) FROM day_reactions) = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(
             (SELECT AVG(r_day) FROM day_reactions)::numeric / lm.members_count * 100, 4)
    END,
    lm.members_count::bigint
FROM posts p
CROSS JOIN latest_members lm
GROUP BY lm.members_count;
$$;


-- agg_reactions: Love Rate (1.7) и Talk Rate (1.8).
CREATE OR REPLACE FUNCTION agg_reactions(p_date_from date, p_date_to date)
RETURNS TABLE (
    love_rate  numeric,
    talk_rate  numeric
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1),
  agg AS (
      SELECT
          SUM(likes_count)    AS total_likes,
          SUM(comments_count) AS total_comments,
          COUNT(*)            AS n_posts
        FROM posts_view
       WHERE post_date BETWEEN p_date_from AND p_date_to
  )
SELECT
    -- Love Rate: Σlikes / (N × n) × 100
    CASE WHEN agg.n_posts = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(agg.total_likes::numeric / (agg.n_posts * lm.members_count) * 100, 4)
    END,
    -- Talk Rate: Σcomments / (N × n) × 100
    CASE WHEN agg.n_posts = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(agg.total_comments::numeric / (agg.n_posts * lm.members_count) * 100, 4)
    END
FROM agg CROSS JOIN latest_members lm;
$$;


-- agg_visibility: VRpost (1.9) и VRday (1.10).
CREATE OR REPLACE FUNCTION agg_visibility(p_date_from date, p_date_to date)
RETURNS TABLE (
    vr_post  numeric,
    vr_day   numeric
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1),
  agg AS (
      SELECT
          SUM(views_count) AS total_views,
          COUNT(*)         AS n_posts,
          COUNT(DISTINCT post_date) AS n_days
        FROM posts_view
       WHERE post_date BETWEEN p_date_from AND p_date_to
  )
SELECT
    -- VRpost: ΣV / (N × n) × 100
    CASE WHEN agg.n_posts = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(agg.total_views::numeric / (agg.n_posts * lm.members_count) * 100, 4)
    END,
    -- VRday: ΣV / (n × d) × 100
    CASE WHEN agg.n_days = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(agg.total_views::numeric / (lm.members_count * agg.n_days) * 100, 4)
    END
FROM agg CROSS JOIN latest_members lm;
$$;


-- agg_content_type: ERcontent по типам (формула 1.11).
CREATE OR REPLACE FUNCTION agg_content_type(p_date_from date, p_date_to date)
RETURNS TABLE (
    content_type    text,
    er_content      numeric,
    posts_count     bigint,
    avg_reactions   numeric
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1),
  by_type AS (
      SELECT
          pv.content_type,
          SUM(pv.reactions_total) AS total_r,
          COUNT(*)                AS n_posts,
          AVG(pv.reactions_total) AS avg_r
        FROM posts_view pv
       WHERE pv.post_date BETWEEN p_date_from AND p_date_to
       GROUP BY pv.content_type
  )
SELECT
    bt.content_type,
    CASE WHEN bt.n_posts = 0 OR lm.members_count = 0
         THEN NULL
         ELSE ROUND(bt.total_r::numeric / (bt.n_posts * lm.members_count) * 100, 4)
    END,
    bt.n_posts::bigint,
    ROUND(bt.avg_r, 2)
FROM by_type bt CROSS JOIN latest_members lm
ORDER BY 2 DESC NULLS LAST;
$$;


-- top_posts: Топ-N публикаций по ERpost (формула 1.1).
CREATE OR REPLACE FUNCTION top_posts(p_date_from date, p_date_to date, p_limit int DEFAULT 10)
RETURNS TABLE (
    post_id       bigint,
    group_id      bigint,
    posted_at     timestamptz,
    content_type  text,
    text_preview  text,
    views_count   int,
    likes_count   int,
    comments_count int,
    reposts_count  int,
    reactions_total int,
    er_post       numeric,
    url           text
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1)
SELECT
    pv.post_id::bigint,
    pv.group_id::bigint,
    pv.posted_at,
    pv.content_type,
    LEFT(pv.text, 200)          AS text_preview,
    pv.views_count,
    pv.likes_count,
    pv.comments_count,
    pv.reposts_count,
    pv.reactions_total,
    CASE WHEN lm.members_count = 0
         THEN NULL
         ELSE ROUND(pv.reactions_total::numeric / lm.members_count * 100, 4)
    END                         AS er_post,
    'https://vk.com/wall-' || pv.group_id || '_' || pv.post_id AS url
FROM posts_view pv
CROSS JOIN latest_members lm
WHERE pv.post_date BETWEEN p_date_from AND p_date_to
ORDER BY er_post DESC NULLS LAST
LIMIT p_limit;
$$;


-- erday_series: ERday по дням для графика динамики.
CREATE OR REPLACE FUNCTION erday_series(p_date_from date, p_date_to date)
RETURNS TABLE (
    post_date  date,
    er_day     numeric
) LANGUAGE sql STABLE AS $$
WITH
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1),
  daily AS (
      SELECT post_date, SUM(reactions_total) AS r_day
        FROM posts_view
       WHERE post_date BETWEEN p_date_from AND p_date_to
       GROUP BY post_date
  )
SELECT
    d.post_date,
    CASE WHEN lm.members_count = 0
         THEN NULL
         ELSE ROUND(d.r_day::numeric / lm.members_count * 100, 4)
    END
FROM daily d CROSS JOIN latest_members lm
ORDER BY d.post_date;
$$;


-- heatmap_views: Средние просмотры по ячейке день_недели × час.
CREATE OR REPLACE FUNCTION heatmap_views(p_date_from date, p_date_to date)
RETURNS TABLE (
    day_of_week  int,
    hour_of_day  int,
    avg_views    numeric
) LANGUAGE sql STABLE AS $$
SELECT
    day_of_week,
    hour_of_day,
    ROUND(AVG(views_count), 2) AS avg_views
FROM posts_view
WHERE post_date BETWEEN p_date_from AND p_date_to
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day;
$$;


-- =============================================================================
-- daily_absolute: суммарные показатели по дням для спарклайнов.
-- =============================================================================
CREATE OR REPLACE FUNCTION daily_absolute(p_date_from date, p_date_to date)
RETURNS TABLE (
    post_date        date,
    total_views      bigint,
    total_reactions  bigint,
    total_comments   bigint,
    total_reposts    bigint,
    posts_count      bigint
) LANGUAGE sql STABLE AS $$
SELECT
    post_date,
    SUM(views_count)::bigint,
    SUM(reactions_total)::bigint,
    SUM(comments_count)::bigint,
    SUM(reposts_count)::bigint,
    COUNT(*)::bigint
FROM posts_view
WHERE post_date BETWEEN p_date_from AND p_date_to
GROUP BY post_date
ORDER BY post_date;
$$;


-- =============================================================================
-- subscribers_delta: динамика подписчиков за период.
-- Использует таблицу groups_raw как историю снапшотов подписчиков.
-- =============================================================================
CREATE OR REPLACE FUNCTION subscribers_delta(p_group_id bigint, p_date_from date, p_date_to date)
RETURNS TABLE (
    n_start  bigint,
    n_end    bigint,
    delta    bigint,
    delta_pct numeric
) LANGUAGE sql STABLE AS $$
WITH
  snap_start AS (
      SELECT members_count
        FROM groups_raw
       WHERE group_id = p_group_id
         AND snapshot_at::date <= p_date_from
       ORDER BY snapshot_at DESC
       LIMIT 1
  ),
  snap_end AS (
      SELECT members_count
        FROM groups_raw
       WHERE group_id = p_group_id
         AND snapshot_at::date <= p_date_to
       ORDER BY snapshot_at DESC
       LIMIT 1
  )
SELECT
    COALESCE(s.members_count, e.members_count)::bigint AS n_start,
    e.members_count::bigint                            AS n_end,
    (e.members_count - COALESCE(s.members_count, e.members_count))::bigint AS delta,
    CASE WHEN COALESCE(s.members_count, 0) = 0 THEN NULL
         ELSE ROUND(
             (e.members_count - s.members_count)::numeric / s.members_count * 100, 2
         )
    END AS delta_pct
FROM snap_end e
LEFT JOIN snap_start s ON true;
$$;


-- =============================================================================
-- erday_series_prev: ERday по дням для предыдущего периода той же длины.
-- =============================================================================
CREATE OR REPLACE FUNCTION erday_series_prev(p_date_from date, p_date_to date)
RETURNS TABLE (
    post_date  date,
    er_day     numeric
) LANGUAGE sql STABLE AS $$
WITH
  delta AS (SELECT p_date_to - p_date_from AS days),
  prev_from AS (SELECT p_date_from - (SELECT days FROM delta) - 1 AS d),
  prev_to   AS (SELECT p_date_from - 1 AS d),
  latest_members AS (SELECT members_count FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1),
  daily AS (
      SELECT post_date, SUM(reactions_total) AS r_day
        FROM posts_view
       WHERE post_date BETWEEN (SELECT d FROM prev_from) AND (SELECT d FROM prev_to)
       GROUP BY post_date
  )
SELECT
    d.post_date,
    CASE WHEN lm.members_count = 0 THEN NULL
         ELSE ROUND(d.r_day::numeric / lm.members_count * 100, 4)
    END
FROM daily d CROSS JOIN latest_members lm
ORDER BY d.post_date;
$$;


-- =============================================================================
-- views_series: суммарные просмотры по дням (текущий период).
-- =============================================================================
CREATE OR REPLACE FUNCTION views_series(p_date_from date, p_date_to date)
RETURNS TABLE (
    post_date    date,
    total_views  bigint
) LANGUAGE sql STABLE AS $$
SELECT post_date, SUM(views_count)::bigint AS total_views
FROM posts_view
WHERE post_date BETWEEN p_date_from AND p_date_to
GROUP BY post_date
ORDER BY post_date;
$$;


-- =============================================================================
-- views_series_prev: суммарные просмотры по дням для предыдущего периода.
-- =============================================================================
CREATE OR REPLACE FUNCTION views_series_prev(p_date_from date, p_date_to date)
RETURNS TABLE (
    post_date    date,
    total_views  bigint
) LANGUAGE sql STABLE AS $$
WITH
  delta     AS (SELECT p_date_to - p_date_from AS days),
  prev_from AS (SELECT p_date_from - (SELECT days FROM delta) - 1 AS d),
  prev_to   AS (SELECT p_date_from - 1 AS d)
SELECT post_date, SUM(views_count)::bigint AS total_views
FROM posts_view
WHERE post_date BETWEEN (SELECT d FROM prev_from) AND (SELECT d FROM prev_to)
GROUP BY post_date
ORDER BY post_date;
$$;
