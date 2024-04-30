# This file is part of periodicos-ws
# Copyright Waynalabs 2023 (R)

import os
import click
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from common.constants import ABS_PATHS, datafiles_for_data_apps
import pandas as pd

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import insert, select, update, func
from sqlalchemy import text


DATABASE_URL = "postgresql://postgres:postgres@localhost/periodicos"

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create a base class for declarative models
Base = declarative_base()

### TABLAS ###
class Newspapers(Base):
    __tablename__ = 'newspapers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    min_date = Column(Date)
    max_date = Column(Date)
    articles = relationship("Articles", backref="newspapers")


class Articles(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    newspaper_id = Column(Integer, ForeignKey('newspapers.id'))
    title = Column(String)
    description = Column(String)
    content = Column(String)
    url = Column(String)
    date_published = Column(Date)
    date_obtained = Column(Date)


class Authors(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    
class ArticlesAuthors(Base):
    __tablename__ = 'articles_authors'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    author_id = Column(Integer, ForeignKey('authors.id'))


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class ArticlesCategories(Base):
    __tablename__ = 'articles_categories'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    category_id = Column(Integer, ForeignKey('category.id'))


class NewsAgencies(Base):
    __tablename__ = 'news_agencies'
    id = Column(Integer, primary_key=True)
    newspaper_id = Column(Integer, ForeignKey('newspapers.id'))
    name = Column(String)


class NerCount(Base):
    __tablename__ = 'ner_counts'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    article_field = Column(String)
    entity = Column(String)
    entity_type = Column(String)
    entity_count = Column(Integer)


def insert_articles_into_db(connection):
    print(" ============== Inserting Articles to database ============")
    print()
    skipped = 0
    inserted = 0
    # Loading every CSV file and inserting into the DB.
    for newspaper_name in datafiles_for_data_apps.keys():
        print()
        print("============================================")
        print(f"=========={newspaper_name}==================")
        print("============================================")
        # TODO: Insert as Bulk and with a given number of records as a batch
        # Before performing the Bulk insert it might be good to drop indexes and recreate
        # them after all bulk insertions.
        try:
            df_norm = pd.read_csv(datafiles_for_data_apps[newspaper_name]["normalized"])

            newspaper_id = 0
            try:
                result = connection.execute(select(Newspapers).where(Newspapers.name == newspaper_name))
                newspaper_id = result.first()._asdict()["id"]
                print(f"newspaper found: {newspaper_id}")
            except Exception as E:
                print(E)

            if newspaper_id == 0:
                print(f"Not found newspaper {newspaper_name}, skipping.)")
                continue

            for index, row in df_norm.iterrows():
                print(f"article - {index}/{len(df_norm)}: {row['title']}...")
                if index % 500 == 0:
                    print(f"inserted: {inserted}, skipped: {skipped}")

                # Checking if the article exists
                try:
                    result = connection.execute(
                        select(Articles)
                        .where(Articles.title == row["title"]))
                    if len(result.all()) > 0:
                        skipped += 1
                        continue
                except Exception as E:
                    print(f"Error getting article {row['title']}")
                    print(E)

                try:
                    description = ""
                    if "description" in row.keys():
                        description = row["description"]

                    insert_statement = insert(Articles).values(
                        newspaper_id=newspaper_id,
                        title=row["title"],
                        description=description,
                        content=row["normalized_content"],
                        url=row["url"],
                        date_published=datetime.strptime(str(row["date"]), '%Y-%m-%d'),
                        date_obtained=datetime.now()
                    )
                    cursor = connection.execute(insert_statement)
                    connection.commit()
                    inserted += 1
                    result = connection.execute(select(Articles).
                                                          where(Articles.title == row["title"]))
                    article_id = result.first()._asdict()["id"]

                    # Inserting categories
                    categories = row["categories"].split(",") if row["categories"] != "" else []
                    if len(categories) > 0:
                        for category in categories:
                            category = category.lower().strip()
                            try:
                                result = connection.execute(select(Categories)
                                                            .where(Categories.name == category))
                                categories_found = result.all()
                                if len(categories_found) == 0:
                                    # new category
                                    insert_statement = insert(Categories).values(name=category)
                                    connection.execute(insert_statement)
                                    connection.commit()

                                    result = connection.execute(select(Categories).
                                                                where(Categories.name == category))
                                    category_id = result.first()._asdict()["id"]
                                    print(f"  inserted new category: {category}")
                                else:
                                    category_id = categories_found[0][0]

                                # relationship article_category
                                insert_statement = insert(ArticlesCategories).values(
                                    article_id=article_id,
                                    category_id=category_id
                                )
                                connection.execute(insert_statement)
                                connection.commit()

                            except Exception as E:
                                print(f"Error inserting category: {E}")

                    # Insert authors
                    if str(row["author"]) != "nan":
                        try:
                            author = row["author"].lower().strip()
                            result = connection.execute(select(Authors)
                                               .where(Authors.name == author))
                            authors_found = result.all()
                            if len(authors_found) == 0:
                                # new author._
                                insert_statement = insert(Authors).values(name=author)
                                connection.execute(insert_statement)
                                connection.commit()

                                result = connection.execute(select(Authors).
                                                            where(Authors.name == author))
                                author_id = result.first()._asdict()["id"]
                                print(f"  inserted new author: {author}")
                            else:
                                author_id = authors_found[0][0]

                            # relationship articles_authors
                            insert_statement = insert(ArticlesAuthors).values(
                                article_id = article_id,
                                author_id = author_id
                            )
                            connection.execute(insert_statement)
                            connection.commit()

                        except Exception as E:
                            print(f"Error inserting author: {E}")

                    # TODO: Check new_agencies
                except Exception as E:
                    print(f"Error on article: {E}")

        except Exception as E:
            print(f"ERROR reading newspaper {newspaper_name}")
            print(E)
            print()

    print("=====================================================")
    print(f"Inserted: {inserted}")
    print("Finished articles insertion.")


def perform_ner_count(connection):
    print("===============Starting NER count to database.===============")
    skipped = 0
    inserted = 0
    for newspaper_name in datafiles_for_data_apps.keys():
        print(f"Processing for {newspaper_name}**")
        for ner_count_file in datafiles_for_data_apps[newspaper_name]["ner_count_names"]:
            print(f"File {ner_count_file}------")
            df_nercount = pd.read_csv(ner_count_file)

            # ejemplo extraer description de eldeber_ner_count_description.csv
            article_field = ner_count_file.split(".csv")[0].split("_")[2]

            previous_title = ""
            article_id = 0

            for index, row in df_nercount.iterrows():
                if (index % 400) == 0:
                    print(f"Inserted: {inserted}, Skipped: {skipped}")

                title = row['title']

                if previous_title != title:
                    previous_title = title
                    # buscando artículo
                    try:
                        result = connection.execute(select(Articles).
                                                    where(Articles.title == title))
                        article_id = result.first()._asdict()["id"]
                    except Exception as E:
                        print(f"Error with article '{row['title']}' --> {article_id}")
                        print(E)
                        continue

                # Verificando que registro no existe
                result = connection.execute(select(NerCount).
                                            where(NerCount.article_id == article_id).
                                            where(NerCount.entity == row["entity"]).
                                            where(NerCount.article_field == article_field))
                if len(result.all()) > 0:
                    skipped += 1
                    continue

                # insertando registro
                try:
                    print(f"{index}/{len(df_nercount)}: {title}")
                    # csv tiene title, type, entity, count
                    insert_statement = insert(NerCount).values(
                        article_id=int(article_id),
                        article_field=article_field,
                        entity=row["entity"],
                        entity_type=row["type"],
                        entity_count=int(row["count"])
                    )
                    cursor = connection.execute(insert_statement)
                    connection.commit()

                    inserted += 1
                except Exception as E:
                    print(f"Error inserting ner record: {row}")
                    print(E)


def update_indexes(connection):
    print("==== Updating indexes ======")

    print(" Min Max Date by newspaper Update.")
    # Update min_date and max_date for each newspaper
    min_max_results = None
    try:
        result = connection.execute(
            text("""
              SELECT MAX(date_published), MIN(date_published), newspaper_id
              FROM articles
              GROUP BY newspaper_id
              ORDER BY newspaper_id
            """))
        min_max_results = result.all()
        print(result.all())
    except Exception as E:
        print("Error updating newspapers min max")
        print(E)
        raise E

    try:
        for row in min_max_results:
            print(row)
            # TODO terminar
            insert_statement = update(Newspapers).where(
                Newspapers.id==row[2] # newspaper_id
            ).values(
                max_date = row[0],
                min_date = row[1],
            )
            print(insert_statement)
            cursor = connection.execute(insert_statement)
            connection.commit()
            print(f"Updated {row}")
    except Exception as E:
        print("Error updating newspapers min max")
        print(E)
        raise E

    try:
        result = connection.execute(text("DROP INDEX idx_articles_title"))
        print(result)
    except Exception as E:
        print("Error occurred while dropping idx_articles_title")
        print(E)
        raise E

    try:
        result = connection.execute(text("CREATE INDEX idx_articles_title ON articles(title)"))
        print(result)
    except Exception as E:
        print("Error occurred on: CREATE INDEX idx_articles_title ON articles(title)")
        print(E)
        raise E

    try:
        result = connection.execute(text("""
        UPDATE articles SET search_vector =
          to_tsvector('spanish', LOWER(title)||' '||content||' '||LOWER(description))"""))
        print(result)
    except Exception as E:
        print("Error occurred updating search_vector")
        print(E)
        raise E

    try:
        result = connection.execute(text("DROP INDEX articles_search_vector_idx"))
        print(result)
    except Exception as E:
        print("Error occurred on: DROP INDEX articles_search_vector_idx")
        print(E)
        raise E

    try:
        result = connection.execute(text("""
        CREATE INDEX articles_search_vector_idx ON articles USING gin(search_vector)
        """))
        print(result.all)
        print("Finished updating indexes")
    except Exception as E:
        print("Error occurred on: CREATE INDEX articles_search_vector_idx ON articles USING gin(search_vector)")
        print(E)
        raise E


@click.command()
@click.option("--insert_articles_to_db", "-i",
              is_flag=True, help="Insert Articles to Database")
@click.option("--ner_count", "-n",
              is_flag=True, help="Run NER count")
def cli(insert_articles_to_db, ner_count):
    with engine.connect() as connection:
        if insert_articles_to_db:
            insert_articles_into_db(connection)
        if ner_count:
            perform_ner_count(connection)
        update_indexes(connection)
        
        # Close the connection
        connection.close()
        print("Finished.")


if __name__ == "__main__":
    print("====== import from csv ===========")
    cli()
