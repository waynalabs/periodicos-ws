"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

from collections import namedtuple
from rest_framework import permissions, renderers, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.http import JsonResponse

from ws.models import Newspapers, Articles, Authors, Categories, NewsAgencies
#from snippets.permissions import IsOwnerOrReadOnly
from ws.serializers import NewspaperSerializer, NewspapersSerializer, \
    ArticlesSerializer, ArticleSerializer


def customJsonResponse(status_code=404, custom_message='Resource not found.', exception=None):
    """Returns a Json respone with a given status code""" 
    return JsonResponse({
        'status_code': status_code,
        'custom_message': custom_message
    })


@api_view(["GET"])
def api_root(request, format=None):
    return Response({
        "newspaper": reverse("newspaper", request=request, format=format),
        "newspapers": reverse("newspapers", request=request, format=format),
        "articles": reverse("articles", request=request, format=format),
        "article": reverse("article", request=request)
    })


class NewspaperView(views.APIView):

    def get(self, request):
        name = request.query_params.get("name", None)
        start_date = request.query_params.get("startDate", None)
        end_date = request.query_params.get("endDate", None)

        # TODO: Validate date params
        
        where_statement = ""
        if name is not None:
            where_statement = f"WHERE n.name = '{name}'"
        else:
            return customJsonResponse(404, f"Newspaper with name {name}, not found.")

        if start_date is not None and end_date is not None:
            where_statement += f"""
            AND a.date_published > '{start_date}'::DATE
            AND a.date_published < '{end_date}'::DATE
            """
        sql = f"""
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
        LEFT JOIN
            articles a ON n.id = a.newspaper_id
        LEFT JOIN
            authors au ON a.id = au.article_id
        LEFT JOIN categories cat ON cat.article_id = au.article_id
        {where_statement}
        GROUP BY
            n.id, n.name
        """
        query_result = list(Newspapers.objects.raw(sql))

        serializer = NewspaperSerializer({
            "id": query_result[0].id,
            "name": query_result[0].name,
            "article_count": query_result[0].article_count,
            "author_count": query_result[0].author_count,
            "categories_count": query_result[0].categories_count,
            "categories": query_result[0].categories,
            "authors": query_result[0].authors,
        })
        return Response(serializer.data)


class ArticlesView(views.APIView, LimitOffsetPagination):

    def get(self, request):
        newspaper = request.query_params.get("newspaper", None)
        start_date = request.query_params.get("startDate", None)
        end_date = request.query_params.get("endDate", None)

        self.max_limit = 1000

        # TODO: Validate date params
        where_statement = ""
        newspapers = []
        if newspaper is None:
            return customJsonResponse(404, f"Newspaper with name {newspaper}, not found.")

        try:
            found_newspaper = Newspapers.objects.get(name=newspaper)
        except Exception as E:
            print(E)
            return customJsonResponse(404, f"Newspaper with name {newspaper}, not found.")

        articles = []
        if start_date is not None and end_date is not None:
            articles = list(
                Articles.objects.filter(newspaper_id=found_newspaper.id)
                .filter(date_published__gte=start_date)
                .filter(date_published__lte=end_date)
            )
        else:
            articles = Articles.objects.filter(newspaper_id=found_newspaper.id)

        results = self.paginate_queryset(
            articles,
            request, view=self
        )

        serializer = ArticlesSerializer({
            "total":  self.count,
            "limit": self.limit,
            "offset": self.offset,
            "articles": results,
        })
        return Response(serializer.data)

class ArticleView(views.APIView):

    def get(self, request):
        id = request.query_params.get("id", None)

        # TODO: validate that id is integer

        if id is None:
            return customJsonResponse(400, "Must specify 'id' as query param.")
        
        article = None
        try:
            article = Articles.objects.get(pk=id)
        except Exception as E:
            print(E)
            return customJsonResponse(404, f"Article with Id {id}, not found.")

        newspaper = Newspapers.objects.get(pk=article.newspaper_id)
        
        categories = Categories.objects.filter(article_id=article.id)
        authors = Authors.objects.filter(article_id=article.id)

        serializer = ArticleSerializer({
            "id": article.id,
            "newspaper": newspaper.name,
            "title": article.title,
            "url": article.url,
            "content_length": len(article.content),
            "description": article.description,
            "authors": [author.name for author in authors],
            "categories": [category.name for category in categories],
            "date_published": article.date_published
        })
        return Response(serializer.data)

        
class NewspapersViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    model = Newspapers
    queryset = Newspapers.objects.all()
    serializer_class = NewspapersSerializer


class ArticlesViewSet(viewsets.ModelViewSet):
    queryset = Articles.objects.all() # update this

# class SnippetViewSet(viewsets.ModelViewSet):
#     """
#     This viewset automatically provides `list`, `create`, `retrieve`,
#     `update` and `destroy` actions.

#     Additionally we also provide an extra `highlight` action.
#     """
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = (
#         permissions.IsAuthenticatedOrReadOnly,
#         IsOwnerOrReadOnly, )

#     @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
#     def highlight(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)

#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset automatically provides `list` and `detail` actions.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
