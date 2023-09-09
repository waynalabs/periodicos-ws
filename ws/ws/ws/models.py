"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

from django.db import models


class Newspapers(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True, null=False)
    min_date = models.DateField()
    max_date = models.DateField()
        
    class Meta:
        db_table = "newspapers"

    
class Articles(models.Model):
    id = models.IntegerField(primary_key=True)
    newspaper_id = models.ForeignKey("ws.newspapers", on_delete=models.CASCADE)
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
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, null=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "authors"


class Categories(models.Model):
    id = models.IntegerField(primary_key=True)
    newspaper = models.ForeignKey(Newspapers, on_delete=models.CASCADE, db_column="newspaper_id", null=True)
    article = models.ForeignKey(Articles, db_column="article_id", on_delete=models.CASCADE, null=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "categories"


class NewsAgencies(models.Model):
    id = models.IntegerField(primary_key=True)
    newspaper_id = models.ForeignKey("ws.newspapers", on_delete=models.CASCADE, null=True)
    name = models.TextField(null=False)

    class Meta:
        db_table = "news_agencies"



