from unicodedata import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("bid/<int:item_id>", views.bidding, name="bidding"),
    path("watchlist/<int:item_id>", views.watchlist, name="watchlist"),
    path("myWatchlist", views.myWatchlist, name="myWatchlist"),
    path("comment/<int:item_id>", views.add_comment, name="add_comment"),
    path("close/<int:item_id>", views.close, name="close")
]
