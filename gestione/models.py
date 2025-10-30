from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.db.models.signals import post_save 
from django.dispatch import receiver 
import datetime # <-- ECCO LA CORREZIONE

# --- PROFILO UTENTE (PER COSTO ORARIO) ---
class ProfiloUtente(models.Model):
    utente = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    costo_orario = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=25.00, 
        verbose_name="Costo Orario (€)"
    )
    def __str__(self):
        return f"Profilo di {self.utente.username} - €{self.costo_orario}/ora"

# Segnale corretto per creare/aggiornare il profilo utente
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfiloUtente.objects.get_or_create(utente=instance)
    else:
        try:
            profilo, created = ProfiloUtente.objects.get_or_create(utente=instance)
            if not created:
                profilo.save() 
        except ProfiloUtente.DoesNotExist:
             ProfiloUtente.objects.create(utente=instance)


# --- MODELLI DI BUSINESS ---
class CategoriaMerceologica(models.Model):
    """
    Rappresenta le categorie di PRODOTTO (es. Cucine, Zona Giorno, Notte, Complementi).
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome Categoria Merceologica")
    class Meta:
        verbose_name = "Categoria Merceologica (Prodotto)"
        verbose_name_plural = "Categorie Merceologiche (Prodotti)"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class CategoriaServizio(models.Model):
    """
    Rappresenta le categorie di ATTIVITA/SERVIZIO (es. Progettazione, Montaggio, Trasporto, Commerciale).
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome Categoria Servizio")
    class Meta:
        verbose_name = "Categoria Servizio (Attività)"
        verbose_name_plural = "Categorie Servizi (Attività)"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Vendita(models.Model):
    """
    Rappresenta la VENDITA PRINCIPALE (il prodotto, es. la Cucina).
    """
    descrizione = models.CharField(max_length=255, verbose_name="Descrizione Prodotto/Servizio")
    categoria = models.ForeignKey(CategoriaMerceologica, on_delete=models.PROTECT, verbose_name="Categoria Merceologica")
    prezzo_vendita = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prezzo di Vendita (€)")
    costo_acquisto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo di Acquisto (€)")
    data_vendita = models.DateField(verbose_name="Data Vendita")
    cliente = models.CharField(max_length=150, blank=True, null=True, verbose_name="Cliente (Opzionale)")
    venditore = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Venditore")
    flag_finanziamento = models.BooleanField(default=False, verbose_name="Finanziamento Attivo")
    flag_reso = models.BooleanField(default=False, verbose_name="Reso Effettuato")
    flag_ritardo_consegna = models.BooleanField(default=False, verbose_name="Ritardo Consegna Segnalato")
    class Meta:
        verbose_name = "Vendita (Prodotto)"
        verbose_name_plural = "Vendite (Prodotti)"
        ordering = ['-data_vendita']
    def __str__(self):
        return f"[{self.data_vendita}] {self.descrizione} - €{self.prezzo_vendita}"
    @property
    def margine_lordo_unitario(self) -> Decimal:
        return self.prezzo_vendita - self.costo_acquisto

class StatMensile(models.Model):
    """
    Contiene solo i costi non calcolabili automaticamente.
    """
    anno = models.PositiveIntegerField(verbose_name="Anno (es. 2024)")
    mese = models.PositiveIntegerField(verbose_name="Mese (1-12)", validators=[MinValueValidator(1), MaxValueValidator(12)])
    costo_marketing_mese = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Costo Marketing/Pubblicità (€)",
        help_text="Costo totale delle campagne pubblicitarie per questo mese."
    )
    costi_operativi_fissi = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Costi Operativi Fissi (€)",
        help_text="Es. affitto, utenze, stipendi fissi (esclusi costi variabili personale)."
    )
    finanziamenti_non_approvati = models.IntegerField(
        default=0, verbose_name="Nr. Finanziamenti Non Approvati",
        help_text="Numero di richieste di finanziamento respinte."
    )
    class Meta:
        verbose_name = "Statistica Mensile Manuale"
        verbose_name_plural = "Statistiche Mensili Manuali"
        unique_together = ('anno', 'mese')
        ordering = ['-anno', '-mese']
    def __str__(self):
        return f"Costi Manuali per {self.mese}/{self.anno}"

class Budget(models.Model):
    anno = models.PositiveIntegerField(verbose_name="Anno (es. 2024)")
    mese = models.PositiveIntegerField(verbose_name="Mese (1-12)", validators=[MinValueValidator(1), MaxValueValidator(12)])
    categoria = models.ForeignKey(CategoriaMerceologica, on_delete=models.CASCADE, verbose_name="Categoria Merceologica")
    obiettivo_vendite_euro = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Budget Vendite (€)")
    obiettivo_margine_percentuale = models.DecimalField(max_digits=5, decimal_places=2, default=30.0, verbose_name="Budget Margine (%)")
    class Meta:
        verbose_name = "Budget Mensile"
        verbose_name_plural = "Budget Mensili"
        unique_together = ('anno', 'mese', 'categoria')
        ordering = ['-anno', '-mese', 'categoria']
    def __str__(self):
        return f"Budget {self.categoria} per {self.mese}/{self.anno}"

class Trattativa(models.Model):
    STATO_LEAD = 'LEAD'
    STATO_APPUNTAMENTO = 'APPUNTAMENTO'
    STATO_PROGETTAZIONE = 'PROGETTAZIONE'
    STATO_PREVENTIVO = 'PREVENTIVO'
    STATO_CONSEGNA = 'IN_CONSEGNA'
    STATO_MONTAGGIO = 'IN_MONTAGGIO'
    STATO_VINTO = 'VINTO'
    STATO_PERSO = 'PERSO'
    STATI_KANBAN_CHOICES = [
        (STATO_LEAD, '1. Lead/Contatto'),
        (STATO_APPUNTAMENTO, '2. Appuntamento Fissato'),
        (STATO_PROGETTAZIONE, '3. Progettazione'),
        (STATO_PREVENTIVO, '4. Preventivo Inviato'),
        (STATO_CONSEGNA, '5. In Consegna'),
        (STATO_MONTAGGIO, '6. In Montaggio'),
        (STATO_VINTO, '7. Chiuso Vinto'),
        (STATO_PERSO, '8. Chiuso Perso'),
    ]
    titolo = models.CharField(max_length=255, verbose_name="Titolo Trattativa")
    cliente_nome = models.CharField(max_length=150, verbose_name="Nome Cliente")
    cliente_contatto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Email/Telefono Cliente")
    valore_stimato = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Valore Prodotto Stimato (€)",
        help_text="Valore di vendita stimato del prodotto principale (es. Cucina)"
    )
    costo_materiali_stimato = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Costo Prodotto Stimato (€)",
        help_text="Costo di acquisto del prodotto principale (COGS)"
    )
    stato = models.CharField(max_length=20, choices=STATI_KANBAN_CHOICES, default=STATO_LEAD, verbose_name="Stato Avanzamento")
    commerciale = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Commerciale Assegnato", related_name="trattative")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_ultimo_aggiornamento = models.DateTimeField(auto_now=True)
    vendita_collegata = models.OneToOneField(Vendita, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vendita Collegata (se vinta)", related_name="trattativa_vinta")
    class Meta:
        verbose_name = "Trattativa"
        verbose_name_plural = "Trattative"
        ordering = ['data_ultimo_aggiornamento']
    def __str__(self):
        return f"[{self.get_stato_display()}] {self.titolo} - {self.cliente_nome}"

class Attivita(models.Model):
    trattativa = models.ForeignKey(Trattativa, on_delete=models.CASCADE, related_name="attivita", verbose_name="Trattativa di Riferimento")
    eseguita_da = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Eseguita da")
    categoria = models.ForeignKey(
        CategoriaServizio, 
        on_delete=models.SET_NULL,
        null=True, blank=False, 
        verbose_name="Categoria Servizio"
    )
    descrizione = models.CharField(max_length=255, verbose_name="Descrizione Attività")
    prezzo_vendita_attivita = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00,
        verbose_name="Prezzo Vendita Servizio (€)",
        help_text="Il prezzo che il cliente paga per questo servizio (es. 300€ per montaggio)"
    )
    tempo_dedicato_ore = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name="Tempo Dedicato (Ore)")
    data_attivita = models.DateField(verbose_name="Data Attività", default=datetime.date.today)
    note = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Attività (Servizio/Costo)"
        verbose_name_plural = "Attività (Servizi/Costi)"
        ordering = ['-data_attivita']
    def __str__(self):
        return f"{self.descrizione} ({self.tempo_dedicato_ore}h) per {self.trattativa.titolo}"

class MessaggioChat(models.Model):
    trattativa = models.ForeignKey(Trattativa, on_delete=models.CASCADE, related_name="messaggi_chat")
    utente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    messaggio = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Messaggio Chat"
        verbose_name_plural = "Messaggi Chat"
        ordering = ['timestamp'] 
    def __str__(self):
        return f"Messaggio di {self.utente} su {self.trattativa.titolo}"