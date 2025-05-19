from django.urls import path
from . import views  # Import views from the current directory

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    # We'll add URLs for query list, detail, create, delete here later
    # Let's add a placeholder for the home page view for now
    path("", views.home, name="home"),
    path("query/new/", views.query_create, name="query_create"),
    path("queries/", views.query_list, name="query_list"),
    path("query/<int:pk>/", views.query_detail, name="query_detail"),
    path("query/<int:pk>/delete/", views.query_delete, name="query_delete"),
]
