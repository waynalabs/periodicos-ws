CREATE TABLE newspapers(
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE NOT NULL,
	min_date DATE,
	max_date DATE
);

INSERT INTO newspapers (name, min_date, max_date) VALUES ('El Deber', '2015-01-01'::DATE, '2023-04-18'::DATE);
INSERT INTO newspapers (name, min_date, max_date) VALUES ('La Razón', '2018-08-23'::DATE, '2023-04-19'::DATE);
INSERT INTO newspapers (name, min_date, max_date) VALUES ('Los tiempos', '2022-05-09'::DATE, '2023-12-02'::DATE);

--SELECT * FROM newspapers;

CREATE TABLE articles(
	id SERIAL PRIMARY KEY,
	newspaper_id INT NOT NULL,
	title TEXT NOT NULL,
	url TEXT,
	description TEXT,
	content TEXT,
	date_published DATE,
	date_obtained DATE,
	FOREIGN KEY (newspaper_id)
      REFERENCES newspapers (id)
);

CREATE TABLE authors (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE articles_authors (
       id SERIAL PRIMARY KEY,
       article_id INT NOT NULL,
       author_id INT NOT NULL,
       FOREIGN KEY (article_id)
         REFERENCES articles (id),
       FOREIGN KEY (author_id)
         REFERENCES authors (id)
);

CREATE TABLE categories (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE articles_categories (
       id SERIAL PRIMARY KEY,
       article_id INT NOT NULL,
       category_id INT NOT NULL,
       FOREIGN KEY (article_id)
         REFERENCES articles (id),
       FOREIGN KEY (category_id)
         REFERENCES categories (id)
);

CREATE TABLE news_agencies (
	id SERIAL PRIMARY KEY,
	newspaper_id INT NULL,
	name TEXT NOT NULL,
	FOREIGN KEY (newspaper_id)
		REFERENCES newspapers (id)
);

-- DROP TABLE newspapers CASCADE;
-- DROP TABLE articles CASCADE;
-- DROP TABLE authors CASCADE;
-- DROP TABLE articles_authors;
-- DROP TABLE categories CASCADE;
-- DROP TABLE articles_categories;
