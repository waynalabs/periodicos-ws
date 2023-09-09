"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""

from collections import namedtuple
from rest_framework import permissions, renderers, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.http import JsonResponse

from ws.models import Newspapers, Articles, Authors, Categories, NewsAgencies
#from snippets.permissions import IsOwnerOrReadOnly
from ws.serializers import NewspaperSerializer, NewspapersSerializer, \
    ArticlesSerializer

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
    })


class NewspaperViewSet(viewsets.ViewSet):
    NewspaperKeyTuple = namedtuple("NewspaperKeyTuple",
                                   ("id", "name", "article_count", "author_count",
                                    "categories_count", "categories", "authors"))

    def retrieve(self, request):
        name = request.query_params.get("name", None)
        start_date = request.query_params.get("startDate", None)
        end_date = request.query_params.get("endDate", None)

        where_statement = ""
        if name is not None:
            where_statement = f"WHERE n.name = '{name}'"
        else:
            return customJsonResponse(404, f"Newspaper with name {name} not found.")
            
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
            COUNT(DISTINCT au.id) AS author_count,
            COUNT(DISTINCT cat.id) AS categories_count
        FROM
            newspapers n
        LEFT JOIN
            articles a ON n.id = a.newspaper_id
        LEFT JOIN
            authors au ON a.id = au.article_id
        LEFT JOIN
	    categories cat ON cat.article_id = a.id        
        {where_statement}
        GROUP BY
            n.id, n.name;
        """
        queryset1 = Newspapers.objects.raw(sql)
        #serializer = NewspaperSerializer(queryset, many=True)
        print(queryset1)
        queryset2 = Categories.objects.filter(newspaper_id=queryset1.id)
        sql = f"""
        SELECT  au.name as authors
        FROM newspapers n
        INNER JOIN articles a ON a.newspaper_id = n.id
        INNER JOIN authors au ON a.id = au.article_id
        WHERE n.id = {queryset1.id}
        """
        queryset3 = Authors.objects.raw(sql)

        serializer = NewspaperSerializer({
            "id": queryset1.id,
            "name": queryset1.name,
            "article_count": queryset1.article_count,
            "author_count": queryset1.author_count,
            "categories_count": queryset1.categories_count,
            "categories": queryset2,
            "authors": queryset3,
        })
        return Response(serializer.data)
        
        


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
            return customJsonResponse(404, f"Newspaper with name {name} not found.")

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
        print(query_result[0])
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

        # sql = f"""
        # SELECT
        #     n.id AS id,
        #     n.name AS name,
        #     COUNT(DISTINCT a.id) AS article_count,
        #     COUNT(DISTINCT au.id) AS author_count,
        #     COUNT(DISTINCT cat.id) AS categories_count
        # FROM
        #     newspapers n
        # LEFT JOIN
        #     articles a ON n.id = a.newspaper_id
        # LEFT JOIN
        #     authors au ON a.id = au.article_id
        # LEFT JOIN
	#     categories cat ON cat.article_id = a.id        
        # {where_statement}
        # GROUP BY
        #     n.id, n.name;
        # """
        # queryset1 = list(Newspapers.objects.raw(sql))
        # queryset2 = Categories.objects.filter(newspaper_id=queryset1[0].id)
        # sql = f"""
        # SELECT au.id, au.name as authors
        # FROM newspapers n
        # INNER JOIN articles a ON a.newspaper_id = n.id
        # INNER JOIN authors au ON a.id = au.article_id
        # WHERE n.id = {queryset1[0].id}
        # """
        # queryset3 = Authors.objects.raw(sql)
        # print(queryset3)
        
        # serializer = NewspaperSerializer({
        #     "id": queryset1[0].id,
        #     "name": queryset1[0].name,
        #     "article_count": queryset1[0].article_count,
        #     "author_count": queryset1[0].author_count,
        #     "categories_count": queryset1[0].categories_count,
        #     "categories": queryset2,
        #     "authors": queryset3,
        # })
        # return Response(serializer.data)


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
    serializer_class = ArticlesSerializer

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
