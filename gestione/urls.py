from django.urls import path, include
from . import views

# Definiamo gli URL specifici per l'app 'gestione'
urlpatterns = [
    # Dashboard principale
    path('', views.dashboard, name='dashboard'),
    # Report performance venditori
    path('venditori/', views.report_venditori, name='report_venditori'),
    
    # Kanban
    path('kanban/', views.kanban_board, name='kanban_board'),
    # API per spostare le card (drag-and-drop)
    path('api/move-trattativa/', views.move_trattativa, name='move_trattativa'),
    
    # URL Modal "Chiudi Vinto"
    path('trattativa/<int:trattativa_id>/chiudi/', 
         views.chiudi_trattativa_modal, 
         name='chiudi_trattativa_modal'),

    # Report Attività
    path('report-attivita/', views.report_attivita, name='report_attivita'),

    # URL Pagina Dettaglio e API HTMX
    path('trattativa/<int:trattativa_id>/', 
         views.trattativa_dettaglio, 
         name='trattativa_dettaglio'), # Gestisce GET e POST (update)
    path('trattativa/<int:trattativa_id>/add-attivita/', 
         views.add_attivita, 
         name='add_attivita'),
    path('trattativa/<int:trattativa_id>/add-messaggio/', 
         views.add_messaggio, 
         name='add_messaggio'),
    
    # URL Statistiche Mensili
    path('statistiche-mensili/', views.statistiche_mensili, name='statistiche_mensili'),

    # URL Nuova Trattativa
    path('nuova-trattativa/', views.nuova_trattativa, name='nuova_trattativa'),

    # --- NUOVI URL (PUNTO 17) ---
    path('lista/', views.trattativa_lista, name='trattativa_lista'),
    path('esporta-excel/', views.esporta_trattative_excel, name='esporta_trattative_excel'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('attivita/<int:attivita_id>/modifica/', views.edit_attivita, name='edit_attivita'),
    path('attivita/<int:attivita_id>/elimina/', views.delete_attivita, name='delete_attivita'),
    path('attivita/calcola-costi/', views.calcola_costi_attivita, name='calcola_costi_attivita'),
]