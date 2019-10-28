BIGQUERY_PUBLIC_DATA_QUERY = """
SELECT
  c.id,
  c.author,
  c.title,
  c.score,
  c.story_time,
  c.url,
  CONCAT(c.author, ', ', c.commenters, ', ') AS commenters,
  CONCAT(c.title, '. ', c.story_text, '. ', c.comments) AS all_text
FROM (
  SELECT
    ANY_VALUE(b.id) AS id,
    ANY_VALUE(b.author) AS author,
    ANY_VALUE(b.title) AS title,
    ANY_VALUE(b.score) AS score,
    ANY_VALUE(b.story_time) AS story_time,
    ANY_VALUE(b.url) AS url,
    ANY_VALUE(b.story_text) AS story_text,
    STRING_AGG(DISTINCT commenter, ', ') AS commenters,
    STRING_AGG(DISTINCT comment, '. ') AS comments
  FROM ((
      SELECT
        DISTINCT a.id,
        a.author,
        a.title,
        a.score,
        a.story_time,
        a.url,
        a.story_text,
        a.commenter1 AS commenter,
        a.comment1 AS comment
      FROM (
        SELECT
          s.id,
          s.author,
          s.title,
          s.score,
          s.story_time,
          s.url,
          s.text AS story_text,
          p2.commenter AS commenter1,
          p2.text AS comment1,
          p1.commenter AS commenter2,
          p1.text AS comment2,
          p0.commenter AS commenter3,
          p0.text AS comment3
        FROM (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p0
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p1
        ON
          p1.id=p0.parent
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p2
        ON
          p2.id=p1.parent
        JOIN (
          SELECT
            id,
            `by` AS author,
            score,
            `timestamp` AS story_time,
            url,
            text,
            title
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'story'
            AND score > 10
            AND `timestamp` > '2011-12-31 23:59:00') s
        ON
          s.id=p2.parent) a)
    UNION ALL (
      SELECT
        DISTINCT a.id,
        a.author,
        a.title,
        a.score,
        a.story_time,
        a.url,
        a.story_text,
        a.commenter2 AS commenter,
        a.comment2 AS comment
      FROM (
        SELECT
          s.id,
          s.author,
          s.title,
          s.score,
          s.story_time,
          s.url,
          s.text AS story_text,
          p2.commenter AS commenter1,
          p2.text AS comment1,
          p1.commenter AS commenter2,
          p1.text AS comment2,
          p0.commenter AS commenter3,
          p0.text AS comment3
        FROM (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p0
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p1
        ON
          p1.id=p0.parent
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p2
        ON
          p2.id=p1.parent
        JOIN (
          SELECT
            id,
            `by` AS author,
            score,
            `timestamp` AS story_time,
            url,
            text,
            title
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'story'
            AND score > 10
            AND `timestamp` > '2011-12-31 23:59:00') s
        ON
          s.id=p2.parent) a)
    UNION ALL (
      SELECT
        DISTINCT a.id,
        a.author,
        a.title,
        a.score,
        a.story_time,
        a.url,
        a.story_text,
        a.commenter3 AS commenter,
        a.comment3 AS comment
      FROM (
        SELECT
          s.id,
          s.author,
          s.title,
          s.score,
          s.story_time,
          s.url,
          s.text AS story_text,
          p2.commenter AS commenter1,
          p2.text AS comment1,
          p1.commenter AS commenter2,
          p1.text AS comment2,
          p0.commenter AS commenter3,
          p0.text AS comment3
        FROM (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p0
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p1
        ON
          p1.id=p0.parent
        JOIN (
          SELECT
            id,
            `by` AS commenter,
            text,
            parent
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'comment') p2
        ON
          p2.id=p1.parent
        JOIN (
          SELECT
            id,
            `by` AS author,
            score,
            `timestamp` AS story_time,
            url,
            text,
            title
          FROM
            `bigquery-public-data.hacker_news.full`
          WHERE
            type LIKE 'story'
            AND score > 10
            AND `timestamp` > '2011-12-31 23:59:00') s
        ON
          s.id=p2.parent) a)) b
  GROUP BY
    b.id) c"""

CREATE_POSTGRES_TABLE_QUERY = """
CREATE TABLE {}(
    id integer PRIMARY KEY,
    author text,
    title text,
    score integer,
    story_time timestamp,
    url text,
    commenters text,
    all_text text
)
"""
