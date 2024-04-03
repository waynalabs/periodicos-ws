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

from ws.models import Newspapers, Articles, Authors, Categories, NewsAgencies, \
    ArticlesAuthors, ArticlesCategories
#from snippets.permissions import IsOwnerOrReadOnly
from ws.serializers import NewspaperSerializer, NewspapersSerializer, \
    ArticlesSerializer, ArticleSerializer, \
    AuthorsSerializer, AuthorSearchSerializer, \
    EntitySearchSerializer, \
    CategorySerializer, \
    TextSearchArticlesSerializer, \
    CategoriesByMonthAndNewspaperSerializer


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
        "article": reverse("article", request=request),
        "authorSearch": reverse("authorSearch", request=request),
        "category": reverse("category", request=request),
        "topCategoriesByMonth": reverse("topCategoriesByMonth", request=request),
        "fullTextSearch": reverse("fullTextSearch", request=request),
        "namedEntitySearch": reverse("namedEntitySearch", request=request),
    })


class NewspaperView(views.APIView):

    def get(self, request):
        """
        Retorna detalles de un periódico en específico.
        """
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
        LEFT JOIN articles a ON n.id = a.newspaper_id
        LEFT JOIN articles_authors aa ON aa.article_id = a.id
        LEFT JOIN authors au ON aa.author_id = au.id
        LEFT JOIN articles_categories ac ON ac.article_id = a.id
        LEFT JOIN categories cat ON ac.category_id = cat.id
        {where_statement}
        GROUP BY
            n.id, n.name
        """
        query_result = list(Newspapers.objects.raw(sql))

        serializer = NewspaperSerializer({
            "id": query_result[0].id,
            "name": query_result[0].name,
            "articles_count": query_result[0].article_count,
            "authors_count": query_result[0].author_count,
            "categories_count": query_result[0].categories_count,
            "authors": query_result[0].authors,
            "categories": query_result[0].categories,
        })
        return Response(serializer.data)


class ArticlesView(views.APIView, LimitOffsetPagination):

    def get(self, request):
        newspaper = request.query_params.get("name", None)
        start_date = request.query_params.get("startDate", None)
        end_date = request.query_params.get("endDate", None)

        self.max_limit = 5000

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
            article = Articles.objects.get(id=id)
        except Exception as E:
            print(E)
            return customJsonResponse(404, f"Article with Id {id}, not found.")

        newspaper = Newspapers.objects.get(pk=article.newspaper_id)

        categories = Categories.objects.raw(f"""
        SELECT a.id, cat.name
          FROM articles a
	  INNER JOIN articles_categories ac ON a.id = ac.article_id
	  INNER JOIN categories cat ON cat.id = ac.category_id
        WHERE a.id = {id}
        """)
        #print(categories)

        authors = Authors.objects.raw(f"""
        SELECT a.id, au.name
          FROM articles a
          INNER JOIN articles_authors ac ON a.id = ac.article_id
          INNER JOIN authors au ON au.id = ac.author_id
        WHERE a.id = {id}
        """)

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


class ArticlesViewSet(viewsets.ModelViewSet, LimitOffsetPagination):
    queryset = Articles.objects.all() # update this


class AuthorSearch(views.APIView, LimitOffsetPagination):

    def get(self, request):
        name = request.query_params.get("name", "").replace("'", "").replace("%", "")

        self.max_limit = 1000

        if name == "":
            return customJsonResponse(400, f"Author name must be specified.")

        found_authors = []
        try:
            found_authors = list(Authors.objects.filter(name__startswith=f"{name.lower()}"))
        except Exception as E:
            return customJsonResponse(404, f"Author with name {name.lower()}, not found.")

        results = self.paginate_queryset(found_authors, request, view=self)
        
        serializer = AuthorSearchSerializer({
            "total":  self.count,
            "limit": self.limit,
            "offset": self.offset,
            "authors": [author.name for author in results]
        })
        return Response(serializer.data)


class CategoryView(views.APIView, LimitOffsetPagination):

    def get(self, request):
        category = request.query_params.get("category", "").replace("'", "").replace("%", "")

        if category == "":
            return customJsonResponse(400, "a category must be specified.")

        self.max_limit = 5000

        try:
            sql = f"""
            WITH filtered_categories AS (
              SELECT
            	a.id, a.title, a.url, a.date_published
              FROM
                categories c
              INNER JOIN articles_categories ac ON c.id = ac.category_id
              INNER JOIN articles a ON a.id = ac.article_id
              WHERE
                c.name ilike '{category}'
            )
            SELECT DISTINCT(id), title, url, date_published
            FROM
              filtered_categories
            ORDER BY date_published DESC
            """
            results = list(Articles.objects.raw(sql))
            articles = self.paginate_queryset(
                results, request, view=self
            )
            serializer = CategorySerializer({
                "total": self.count,
                "limit": self.limit,
                "offset": self.offset,
                "category": category,
                "articles": articles,
            })
            return Response(serializer.data)
        except Exception as E:
            print(E)
            return customJsonResponse(500, "An error occurred during the query.")
            
    
class EntitySearch(views.APIView, LimitOffsetPagination):

    def get(self, request):
        self.max_limit = 2500

        search_text = request.query_params.get("searchText", ""). \
                                          replace("'", "").replace("%", "")
        strict_equal = request.query_params.get("strictEqual", "")

        if search_text == "":
            return customJsonResponse(400, f"A searchText should be specified")

        where_statement = f"WHERE nc.entity ILIKE '{search_text}"
        if strict_equal.lower() == "true" :
            where_statement += "%%'"
        else:
            where_statement += "'"

        sql = f"""
        SELECT a.id,
              a.title, a.url, a.date_published,
              nc.entity_count as ocurrences, nc.entity_type,
              nc.article_field, nc.entity
        FROM articles a
	  INNER JOIN ner_counts nc ON nc.article_id = a.id
	  INNER JOIN newspapers n ON n.id = a.newspaper_id
        {where_statement}
        ORDER BY a.date_published DESC
        """

        query_result = list(Articles.objects.raw(sql))

        results = self.paginate_queryset(
            query_result,
            request, view=self
        )
        serializer = EntitySearchSerializer({
            "total": self.count,
            "limit": self.limit,
            "offset": self.offset,
            "articles": results,
        })
        return Response(serializer.data)


class ArticlesTextSearch(views.APIView, LimitOffsetPagination):

    def get(self, request):
        self.max_limit = 2500
        search_text = request.query_params.get("searchText", ""). \
                                          replace("'", "").replace("%", "")
        rate = request.query_params.get("rate", "9")

        if search_text == "":
            return customJsonResponse(400, f"A searchText should be specified.")
        if len(search_text) < 3 and len(search_text) > 750:
            return customJsonResponse(400, f"The searchText length must be 3 to 750 characters.")
        
        try:
            rate = int(rate)
        except:
            return customJsonResponse(400, f"Only a numeric rate is acepted between 1 and 100.")

        if rate < 1 or rate > 100:
            return customJsonResponse(400, f"Only a numeric rate is accepted between 1 and 100.")
        
        query_rate = rate/100

        sql = f"""
        SELECT id, title, url, date_published,
          ts_rank(search_vector, plainto_tsquery('spanish', '{search_text.lower()}')) as rate
	FROM articles
	WHERE ts_rank(search_vector,
          plainto_tsquery('spanish', '{search_text.lower()}')) >= {query_rate} 
	  AND search_vector @@ plainto_tsquery('spanish', '{search_text.lower()}') 
	ORDER BY rate DESC;
        """

        query_result = list(Articles.objects.raw(sql))

        results = self.paginate_queryset(
            query_result,
            request, view=self
        )
        serializer = TextSearchArticlesSerializer({
            "total": self.count,
            "limit": self.limit,
            "offset": self.offset,
            "min_rate": rate,
            "articles": results,
        })
        return Response(serializer.data)


class TopCategoriesByMonthAndNewspaper(views.APIView):

    def get(self, request):
        newspaper = request.query_params.get("newspaper", "El Deber") \
                                        .replace("'", "").replace("%", "")
        start_date = request.query_params.get("startDate", None)
        end_date = request.query_params.get("endDate", None)

        # TODO: Validate date params

        if start_date is None:
            return customJsonResponse(400, "Must specify startDate in YYYY-MM-DD format")
        if end_date is None:
            return customJsonResponse(400, "Must specify endDate in YYYY-MM-DD format")

        where_statement = f"""
          date_published >= '{start_date}' AND date_published < '{end_date}'
          AND n.name = '{newspaper}'
        """
        try:
            sql = f"""
            with article_category_counts AS (
                SELECT
                    a.newspaper_id,
                    cat.name as category_name, 
                    COUNT(*) AS category_count,
                    (EXTRACT(year from date_published)||'-'||
                     EXTRACT(month from date_published)) as yrm
                FROM
                    articles a
            		LEFT JOIN newspapers n ON n.id = a.newspaper_id
            	    LEFT JOIN articles_categories ac ON a.id = ac.article_id
            		LEFT JOIN categories cat ON ac.category_id = cat.id
            	WHERE {where_statement}
                GROUP BY
                    a.newspaper_id, cat.name,
                      (EXTRACT(year from date_published)||'-'||
                       EXTRACT(month from date_published))
            	ORDER BY category_count DESC
            ),
            ranked_categories AS (
            	SELECT *, ROW_NUMBER() OVER (PARTITION BY newspaper_id,
                  yrm ORDER BY category_count DESC) AS cat_rank
            	FROM article_category_counts
            )
            SELECT n.id, n.name as newspaper, rc.yrm AS year_month,
              rc.category_name, rc.category_count
            FROM ranked_categories rc
            	JOIN newspapers n ON rc.newspaper_id = n.id
            	JOIN categories c ON  rc.category_name = c.name
            WHERE rc.cat_rank <= 3
            ORDER BY rc.yrm DESC;            
            """
            query_result = list(Newspapers.objects.raw(sql))
            serializer = CategoriesByMonthAndNewspaperSerializer({
                "start_date": start_date,
                "end_date": end_date,
                "results": query_result
            })
            return Response(serializer.data)
        except Exception as E:
            print(E)
            return customJsonResponse(500, "Error occured during the query.")
        

    #     newspaper = serializers.CharField()
    # year_month = serializers.CharField()
    # category = serializers.CharField()
    # count = serializers.IntegerField()
    
# class AuthorView(views.APIView, LimitOffsetPagination):

#     def get(self, request):
#         name = request.query_params.get("name", None)

#         self.max_limit = 1000

#         if name is None:
#             return customJsonResponse(404, f"Author name {name}, not found.")

#         try:
#             found_authors = list(Authors.objects.filter(name__istartswith=f"{name}%"))
    
