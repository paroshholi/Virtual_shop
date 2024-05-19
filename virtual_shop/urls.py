"""virtual_shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
import home.views as h
import enter.views as e


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',h.home,name='home'),
    path('add_to_cart/<int:product_id>/', h.add_to_cart, name='add_to_cart'),
    path('add_to_wishlist/<int:product_id>/', h.add_to_wishlist, name='add_to_wishlist'),
    path("register", e.register, name="register"),
    path("login",e.login, name="login"),
    path("logout",e.logout,name="logout"),
    path('wishlist/', h.wishlist_view, name='wishlist'),
    path('cart/', h.cart_view, name='cart'),
    path('remove_from_wishlist/<int:product_id>/', h.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove_from_cart/<int:product_id>/', h.remove_from_cart, name='remove_from_cart'),
    path('product/<int:product_id>/', h.product_detail, name='product_detail'),
    path('search/', h.search_products, name='search_products'),
    path('category/<str:category>/', h.category_view, name='category'),
    path('chatbot/', h.chatbot_response, name='chatbot'),
    path('update_quantity/<int:product_id>/<int:new_quantity>/', h.update_quantity, name='update_quantity'),
    path('confirm_purchase/', h.confirm_purchase, name='confirm_purchase'),
    path('order_history/', h.order_history, name='order_history'),
]

# Only in development, serve media files via Django
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
