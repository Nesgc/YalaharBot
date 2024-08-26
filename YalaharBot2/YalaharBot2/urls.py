from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from bot.views import character_list, character_create, index  # Import index as well

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/characters/', character_list),
    path('api/characters/', character_create),  # Remove methods=['POST']
    re_path(r'^.*', index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static('/static/frontend/', document_root=settings.BASE_DIR / 'frontend' / 'build' / 'static')