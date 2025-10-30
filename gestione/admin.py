from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Categoria, Vendita, StatMensile, Budget, 
    Trattativa, Attivita, MessaggioChat, ProfiloUtente
)

# --- Configurazione per Profilo Utente ---
class ProfiloUtenteInline(admin.StackedInline):
    model = ProfiloUtente
    can_delete = False
    verbose_name_plural = 'Profilo (Costo Orario)'
    fk_name = 'utente'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfiloUtenteInline, )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(ProfiloUtente)
class ProfiloUtenteAdmin(admin.ModelAdmin):
    list_display = ('utente', 'costo_orario')

# --- Registrazioni Esistenti ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Vendita)
class VenditaAdmin(admin.ModelAdmin):
    list_display = (
        'data_vendita', 'descrizione', 'categoria', 
        'prezzo_vendita', 'costo_acquisto', 'get_margine_euro',
        'get_margine_percent', 'venditore', 'flag_finanziamento', 'flag_reso',
    )
    list_filter = (
        'data_vendita', 'categoria', 'venditore', 
        'flag_finanziamento', 'flag_reso', 'flag_ritardo_consegna'
    )
    search_fields = ('descrizione', 'cliente')
    date_hierarchy = 'data_vendita'
    @admin.display(description='Margine (€)')
    def get_margine_euro(self, obj):
        return obj.margine_lordo_unitario
    @admin.display(description='Margine (%)')
    def get_margine_percent(self, obj):
        return f"{obj.margine_percentuale_unitario:.2f}%"

#
# --- MODIFICA (PUNTO 18) ---
# Aggiornato l'admin di StatMensile per rimuovere i campi
# che ora sono calcolati automaticamente.
#
@admin.register(StatMensile)
class StatMensileAdmin(admin.ModelAdmin):
    list_display = (
        'anno', 
        'mese', 
        'costi_operativi_fissi',
        'costo_marketing_mese',
        'finanziamenti_non_approvati',
    )
    list_filter = ('anno',)

    # Rimuovi i fieldset che contenevano campi non più esistenti
    fieldsets = (
        (None, {'fields': ('anno', 'mese')}),
        ('Costi Manuali', {
            'fields': (
                'costi_operativi_fissi', 
                'costo_marketing_mese', 
                'finanziamenti_non_approvati'
            )
        }),
    )

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'anno', 'mese', 'categoria', 
        'obiettivo_vendite_euro', 'obiettivo_margine_percentuale'
    )
    list_filter = ('anno', 'mese', 'categoria')

class AttivitaInline(admin.TabularInline):
    model = Attivita
    extra = 1
    fields = ('data_attivita', 'categoria', 'descrizione', 'tempo_dedicato_ore', 'eseguita_da')

@admin.register(Trattativa)
class TrattativaAdmin(admin.ModelAdmin):
    list_display = (
        'titolo', 'stato', 'cliente_nome', 
        'valore_stimato', 'costo_materiali_stimato', 'commerciale', 'data_ultimo_aggiornamento'
    )
    list_filter = ('stato', 'commerciale', 'data_creazione')
    search_fields = ('titolo', 'cliente_nome')
    inlines = [AttivitaInline]

@admin.register(Attivita)
class AttivitaAdmin(admin.ModelAdmin):
    list_display = (
        'descrizione', 'trattativa', 'categoria', 'data_attivita', 
        'tempo_dedicato_ore', 'eseguita_da'
    )
    list_filter = ('data_attivita', 'eseguita_da', 'categoria')
    search_fields = ('descrizione', 'trattativa__titolo')

@admin.register(MessaggioChat)
class MessaggioChatAdmin(admin.ModelAdmin):
    list_display = ('trattativa', 'utente', 'timestamp', 'messaggio')
    list_filter = ('timestamp', 'utente')
    search_fields = ('messaggio', 'trattativa__titolo')