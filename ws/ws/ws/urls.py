"""
This is part of periodicos-ws
Copyright Waynalabs 2023
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
#from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from ws import views

#router = DefaultRouter()
# router.register(r"newspapers", views.NewspapersViewSet)
# router.register(r"articles", views.ArticlesViewSet)

urlpatterns = [
    path("admin/", admin.site.urls), # review this
    path("api/", views.api_root),
    path("api/newspaper/", views.NewspaperView.as_view(), name="newspaper"),
    path("api/newspapers/", views.NewspapersViewSet.as_view({
        "get": "list"
    }), name="newspapers"),
    path("api/articles/", views.ArticlesView.as_view(), name="articles"),
    path("api/article/", views.ArticleView.as_view(), name="article"),
    path("api/authorSearch", views.AuthorSearch.as_view(), name="authorSearch"),
    path("api/category/", views.CategoryView.as_view(), name="category"),
    path("api/topCategoriesByMonth",
         views.TopCategoriesByMonthAndNewspaper.as_view(),
         name='topCategoriesByMonth'),
    path("api/topAuthorsByMonth",
         views.TopAuthorsByMonthAndNewspaper.as_view(),
         name="topAuthorsByMonth"),
    path("api/fullTextSearch", views.ArticlesTextSearch.as_view(), name="fullTextSearch"),
    path("api/namedEntitySearch", views.EntitySearch.as_view(), name="namedEntitySearch"),
    
    path("schema/", get_schema_view(), name="schema"),
    #path("api/", include(router.urls))
]


