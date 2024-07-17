from django.urls import path
from .views import IndexView, SearchHistoryAPI

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('api/search-history/', SearchHistoryAPI.as_view(), name='search_history_api'),
]
