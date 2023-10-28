# This file is part of periodicos-ws
# Copyright Waynalabs 2023

import os
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
from sqlalchemy import insert, select


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


    
#Create a connection
with engine.connect() as connection:
    # Loading every CSV file and inserting into the DB.

    for newspaper_name in datafiles_for_data_apps.keys():
        print()
        print("============================================")
        print(f"=========={newspaper_name}==================")
        print("============================================")
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
                print(f"Not found newspeper {newspaper_name}, skipping.)")
                continue
            
            for index, row in df_norm.iterrows():
                print(f"article - {index}/{len(df_norm)}: {row['title']}...")
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
    print("Finished articles.")
    print("Starting NER count to database.")

    for newspaper_name in datafiles_for_data_apps.keys():
        print(f"Processing for {newspaper_name}**")
        for ner_count_file in datafiles_for_data_apps[newspaper_name]["ner_count_names"]:
            print(f"File {ner_count_file}")
            df_nercount = pd.read_csv(ner_count_file)

            # ejemplo extraer description de eldeber_ner_count_description.csv
            article_field = ner_count_file.split(".csv")[0].split("_")[2]

            previous_title = ""
            article_id = 0

            for index, row in df_nercount.iterrows():
                title = row['title']
                print(f"article - {index}/{len(df_nercount)}: {title}...")

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
                # insertando registro
                try:
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
                    
                except Exception as E:
                    print(f"Error inserting ner record: {row}")
                    print(E)

    # Close the connection
    connection.close()

    print("Finished.")




