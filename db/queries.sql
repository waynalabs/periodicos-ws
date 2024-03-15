-- number of articles, authors by newspaper

SELECT
    n.id AS newspaper_id,
    n.name AS newspaper_name,
    COUNT(DISTINCT a.id) AS article_count,
    COUNT(DISTINCT au.id) AS author_count
FROM
    newspapers n
LEFT JOIN
    articles a ON n.id = a.newspaper_id
LEFT JOIN
    authors au ON a.id = au.article_id
GROUP BY
    n.id, n.name
ORDER BY
    n.id;
	
-- number of articles, authors, list of categories and authors for a given newspaper in the given date range
SELECT
    n.id AS id,
    n.name AS name,
    COUNT(DISTINCT a.id) AS article_count,
	COUNT(DISTINCT cat.id) AS categories_count,
	COUNT(DISTINCT au.id) AS author_count,
	ARRAY_REMOVE(ARRAY_AGG(DISTINCT(cat.name)), NULL) AS categories,
	ARRAY_REMOVE(ARRAY_AGG(DISTINCT(au.name)), NULL) AS authors
FROM
    newspapers n
LEFT JOIN articles a ON n.id = a.newspaper_id
LEFT JOIN articles_authors aa ON aa.article_id = a.id
LEFT JOIN authors au ON aa.author_id = au.id
LEFT JOIN articles_categories ac ON ac.article_id = a.id
LEFT JOIN categories cat ON ac.category_id = cat.id
WHERE n.name = 'La Razón' 
	AND a.date_published > '2016-01-01'::DATE AND a.date_published < '2022-01-01'::DATE
GROUP BY
    n.id, n.name
ORDER BY
    n.id;



SELECT categories.name, a.title
FROM articles a
INNER JOIN  categories ON categories.article_id = a.id
	AND a.date_published > '2021-01-01'::DATE AND a.date_published < '2021-01-05'::DATE

SELECT * FROM articles where url = 'https://eldeber.com.bo/mundo/24-muertes-violentas-en-ano-nuevo-en-colombia_30138'


-- authors given a newspaper

SELECT  au.name as authors
FROM newspapers n
INNER JOIN articles a ON a.newspaper_id = n.id
INNER JOIN authors au ON a.id = au.article_id
WHERE n.id = 1

--- articles belonging a specific category
WITH filtered_categories AS (
  SELECT
    c.name AS category_name,
	a.id, a.title, a.url
  FROM
    categories c
  INNER JOIN articles_categories ac ON c.id = ac.category_id
  INNER JOIN articles a ON a.id = ac.article_id
  WHERE
    c.name ilike 'bolivia'
)
SELECT DISTINCT(id) as article_id, category_name,  title, url
FROM
  filtered_categories
  
  
-- articles belonging a specific category, returning a column with list of article objects
WITH filtered_categories AS (
  SELECT
	DISTINCT(a.id), a.title, a.url,
    c.name AS category_name
  FROM
    categories c
  INNER JOIN articles_categories ac ON c.id = ac.category_id
  INNER JOIN articles a ON a.id = ac.article_id
  WHERE
    c.name ilike 'bolivia'
)
SELECT fc.category_name, 
	json_agg(json_build_object('id', fc.id, 'title', fc.title, 'url', fc.url))
FROM
  filtered_categories fc
GROUP BY fc.category_name


-- articles and article count for a specific category (includes duplicates)
WITH filtered_categories AS (
  SELECT
    c.name AS category_name,
    COUNT(a.id) AS articles_count,
    json_agg(json_build_object('id', a.id, 'title', a.title, 'url', a.url)) AS articles
  FROM
    categories c
  INNER JOIN articles_categories ac ON c.id = ac.category_id
  INNER JOIN articles a ON a.id = ac.article_id
  WHERE
    c.name = 'bolivia'
  GROUP BY
    c.name
)
SELECT category_name, articles_count, articles
FROM
  filtered_categories
ORDER BY articles_count;

-- ner counts that starts with a given entity 
SELECT a.title, a.url, a.date_published,
	nc.entity_count as ocurrences, nc.entity_type, nc.article_field, nc.entity
FROM articles a
	INNER JOIN ner_counts nc ON nc.article_id = a.id
WHERE nc.entity ILIKE 'evo morales%'
ORDER BY ocurrences DESC

-- ner counts strictly equal to a given entity
SELECT a.title, a.url, a.date_published,
	nc.entity_count as ocurrences, nc.entity_type, nc.article_field as en, nc.entity
FROM articles a
	INNER JOIN ner_counts nc ON nc.article_id = a.id
WHERE nc.entity ILIKE 'evo morales'
ORDER BY ocurrences DESC


SELECT a.title, a.url, a.date_published,
	nc.entity_count as ocurrences, nc.entity_type, nc.article_field as en, nc.entity
FROM articles a
	INNER JOIN ner_counts nc ON nc.article_id = a.id
WHERE nc.entity ILIKE 'Adelaida'
ORDER BY ocurrences DESC


-- articles and authors belonging a specific category
SELECT cat.name, a.url


SELECT * FROM categories LIMIT 5
SELECT * FROM articles_categories

--- miscelaneas
SELECT * FROM categories where name = 'bolivia'

SELECT * FROM authors
SELECT * FROM categories

select COUNT(id) from categories

select COUNT(id) from authors

select count(id) from authors a
	inner join articles_authors aa ON a.id = aa.author_id
	inner join articles ar ON aa.artcile_id = ar.id

select article_id, COUNT(article_id)
from articles_authors
group by article_id
order by COUNT(article_id) desc

select COUNT(c.name) as num_categories, c.name 
from articles_categories
inner join categories c ON c.id = articles_categories.category_id
group by c.name
order by c.name

select COUNT(*) from articles

-- queries
SELECT id, title FROM articles WHERE search_vector @@ to_tsquery('Manfred');

SELECT id, title, url, ts_rank(search_vector, plainto_tsquery('spanish', 'mandred reyes')) as rank
	FROM articles
	WHERE ts_rank(search_vector, plainto_tsquery('spanish', 'mandred reyes')) >= 0.09 AND search_vector @@ plainto_tsquery('spanish', 'mandred reyes') 
	ORDER BY rank DESC;

SELECT id, title, url, ts_rank(search_vector, plainto_tsquery('spanish', 'reyes villa')) as rank
	FROM articles
	WHERE ts_rank(search_vector, plainto_tsquery('spanish', 'reyes villa')) >= 0.09 AND search_vector @@ plainto_tsquery('spanish', 'reyes villa') 
	ORDER BY rank DESC;

-- SELECT id, title FROM articles WHERE search_vector @@ to_tsquery('english', 'search terms');


SELECT * from articles LIMIT 5

SELECT to_tsquery('Manfred')
