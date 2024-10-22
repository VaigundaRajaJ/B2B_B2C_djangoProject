from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('add-seller/', views.add_seller, name='add_seller'),
    path('seller-login/', views.seller_login, name='seller_login'),
    path('add-product/', views.add_product, name='add_product'),
    path('search-items/', views.search_items, name='search_items'),
]

# Add this line to serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


