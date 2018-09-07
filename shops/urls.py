from django.conf.urls import url

from . import views
from .views import ShopView, ShopListView

urlpatterns = [
    url(r'^coffeeshops/(\d+)$', ShopView.as_view()),
    url(r'^coffeeshops$', ShopListView.as_view()),
]
