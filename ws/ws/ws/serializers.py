"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import pagination

from ws.models import Newspapers, Articles, Authors, Categories, NewsAgencies, \
    ArticlesAuthors, ArticlesCategories, NerCounts


class ArticleReducedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Articles
        fields = ("id", "title", "date_published")


class ArticleForCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Articles
        fields = ("id", "title", "url")


class AuthorsSerializer(serializers.Serializer):
    name = serializers.CharField()
    articles_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    categories = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    articles = ArticleReducedSerializer(many=True)

    total = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()


class AuthorSearchSerializer(serializers.Serializer):
    authors = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    total = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()


# class ArticleCategorySerializer    

class CategorySearchSerializer(serializers.Serializer):
    categories = serializers.ListField(
        child=ArticleForCategorySerializer()
    )
    total = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    
    
class CategoriesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categories
        fields = ("name",)


class NewsAgenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NewsAgencies
        fields = "__all__"


class NewspaperSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    articles_count = serializers.IntegerField()
    authors_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    categories = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    authors = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )


class NewspapersSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(
        view_name="newspapers",
        lookup_field="name",
        read_only=True
    )

    class Meta:
        model = Newspapers
        fields = "__all__"
        # extra_kwargs = {
        #     "url": {"view_name": "newspapers", "lookup_field": "id"},
        # }


class ArticlesSerializer(serializers.Serializer, pagination.PageNumberPagination):
    articles = ArticleReducedSerializer(many=True)

    total = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()


class ArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    newspaper = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    content_length = serializers.IntegerField()
    description = serializers.CharField()
    date_published = serializers.DateField()
    categories = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    authors = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    

class ArticleNerCountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    url = serializers.CharField()
    date_published = serializers.DateField()
    ocurrences = serializers.IntegerField()
    entity_type = serializers.CharField()
    article_field = serializers.CharField()
    entity = serializers.CharField()

    
class EntitySearchSerializer(serializers.Serializer, pagination.PageNumberPagination):
    total = serializers.IntegerField()
    offset = serializers.IntegerField()
    limit = serializers.IntegerField()

    articles = ArticleNerCountSerializer(many=True)


    
# class SnippetSerializer(serializers.HyperlinkedModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     highlight = serializers.HyperlinkedIdentityField(
#         view_name='snippet-highlight', format='html')

#     class Meta:
#         model = Snippet
#         fields = ('url', 'id', 'highlight', 'owner', 'title', 'code',
#                   'linenos', 'language', 'style')


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     snippets = serializers.HyperlinkedRelatedField(
#         many=True, view_name='snippet-detail', read_only=True)

#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'snippets')
