"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

from django.db import models


class Newspapers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True, null=False,)
    min_date = models.DateField()
    max_date = models.DateField()
        
    class Meta:
        db_table = "newspapers"

    
class Articles(models.Model):
    id = models.IntegerField(primary_key=True)
    newspaper = models.ForeignKey(Newspapers, on_delete=models.CASCADE) # newspaper_id
    title = models.TextField(null=False)
    url = models.TextField()
    description = models.TextField()
    content = models.TextField()
    date_published = models.DateField()
    date_obtained = models.DateField()

    class Meta:
        db_table = "articles"
        ordering = ["date_published"]


class Authors(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "authors"


class ArticlesAuthors(models.Model):
    id = models.IntegerField(primary_key=True)
    article = models.ForeignKey(Articles, db_column="article_id", on_delete=models.CASCADE, null=True)
    author =models.ForeignKey(Authors, db_column="author_id", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "articles_authors"


class Categories(models.Model):
    id = models.IntegerField(primary_key=True)
    article = models.ForeignKey(Articles, db_column="article_id", on_delete=models.CASCADE, null=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "categories"


class ArticlesCategories(models.Model):
    id = models.IntegerField(primary_key=True)
    article = models.ForeignKey(Articles, db_column="article_id", on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Categories, db_column="category_id", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "articles_categories"


class NewsAgencies(models.Model):
    id = models.IntegerField(primary_key=True)
    newspaper_id = models.ForeignKey("ws.newspapers", on_delete=models.CASCADE, null=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "news_agencies"


class NerCounts(models.Model):
    id = models.IntegerField(primary_key=True)
    article = models.ForeignKey(Articles, db_column="article_id", on_delete=models.CASCADE, null=True)
    article_field = models.TextField(null=False)
    entity = models.TextField(null=False)
    entity_type = models.TextField(null=False)
    entity_count = models.IntegerField(null=False)

    class Meta:
        db_table = "ner_counts"
