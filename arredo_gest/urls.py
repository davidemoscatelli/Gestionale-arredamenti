from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URL di autenticazione (login, logout)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # URL della nostra app 'gestione' (pagina principale, kanban, etc.)
    path('', include('gestione.urls')),
]