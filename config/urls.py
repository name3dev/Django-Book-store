"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from books import views


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.book_list, name="home"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:book_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/plus/<int:book_id>/", views.plus_cart, name="plus_cart"),
    path("cart/minus/<int:book_id>/", views.minus_cart, name="minus_cart"),
    path("cart/remove/<int:book_id>/", views.remove_from_cart, name="remove_from_cart"),

    path("api/books/", views.books_api, name="books_api"),
]