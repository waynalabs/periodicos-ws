"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

# from django.contrib.auth.models import User
from rest_framework import serializers

from ws.models import Newspapers, Articles, Authors, Categories, NewsAgencies


class AuthorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Authors
        fields = ("name",)

        
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
    article_count = serializers.IntegerField()
    author_count = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    categories = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    authors = serializers.ListField(
        child=serializers.CharField(allow_null=True)
    )
    #categories = CategoriesSerializer(many=True, read_only=True, allow_null=True)
    #authors = AuthorsSerializer(many=True, read_only=True, allow_null=True)


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


class ArticlesSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(
        view_name="articles",
        lookup_field="id",
        many=True,
        allow_null=True,
        read_only=True,
    )
    class Meta:
        model = Articles
        fields = "__all__"

        
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
