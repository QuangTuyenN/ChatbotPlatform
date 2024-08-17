from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path('admin/', admin.site.urls),
               path('token/', CustomTokenObtainPairView.as_view(),
                    name='token_obtain_pair'),
               path('token/refresh/', TokenRefreshView.as_view(),
                    name='token_refresh'),
               path('token/verify/', TokenVerifyView.as_view(),
                    name='token_verify'),
               path('schema-ui/', SpectacularAPIView.as_view(), name='schema'),
               path('', SpectacularSwaggerView.as_view(
                   url_name='schema'), name='swagger-ui'),
               path(
                   'docs2/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
               path('api/account/', include('account.urls')),
               path('api/bot/', include('bot.urls.bot_urls')),
               path('api/chitchat/', include('bot.urls.chit_urls')),
               path('api/chit-exp/', include('bot.urls.exp_urls')),
               path('api/intent/', include('bot.urls.int_urls')),
               path('api/entity/', include('bot.urls.entity_urls')),
               path('api/entity-kw/', include('bot.urls.entity_kw_urls')),
               path('api/story/', include('bot.urls.story_urls')),
               path('api/step/', include('bot.urls.step_urls')),
               path('api/intent-exp/', include('bot.urls.int_exp_urls')),
               path('api/action/', include('bot.urls.action_urls')),
               path('api/event/', include('bot.urls.event_urls')),
               path('api/map/', include('mymap.urls.map_urls')),
               path('api/menu/', include('menu.urls.menu_urls'))]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
