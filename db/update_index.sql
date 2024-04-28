-- indices
DROP INDEX idx_articles_title;

CREATE INDEX idx_articles_title ON articles(title);

-- search vector
UPDATE articles SET search_vector = to_tsvector('spanish', LOWER(title) || ' ' || content || ' ' || LOWER(description));
DROP INDEX articles_search_vector_idx
CREATE INDEX articles_search_vector_idx ON articles USING gin(search_vector);

