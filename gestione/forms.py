from django import forms
from .models import (
    Vendita, CategoriaMerceologica, CategoriaServizio, Trattativa, 
    Attivita, MessaggioChat, StatMensile, RuoloCosto
)
from django.contrib.auth.models import User
import datetime

class TrattativaVintaForm(forms.ModelForm):
    # MODIFICA: Ora punta a CategoriaMerceologica
    categoria = forms.ModelChoiceField(
        queryset=CategoriaMerceologica.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    descrizione = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    prezzo_vendita = forms.DecimalField(label="Prezzo Vendita Prodotto (€)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    costo_acquisto = forms.DecimalField(label="Costo Acquisto Prodotto (€)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    data_vendita = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    cliente = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Vendita
        fields = ['descrizione', 'categoria', 'prezzo_vendita', 'costo_acquisto', 'data_vendita', 'cliente', 'flag_finanziamento', 'flag_reso']
        widgets = {'flag_finanziamento': forms.CheckboxInput(attrs={'class': 'form-check-input'}), 'flag_reso': forms.CheckboxInput(attrs={'class': 'form-check-input'})}

class AttivitaForm(forms.ModelForm):
    """
    MODIFICATO: Punta a CategoriaServizio e include prezzo_vendita_attivita
    """
    categoria = forms.ModelChoiceField(
        label="Categoria Servizio",
        queryset=CategoriaServizio.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}) 
    )
    descrizione = forms.CharField(label="Descrizione Attività", widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    prezzo_vendita_attivita = forms.DecimalField(
        label="Prezzo Vendita Servizio (€)",
        initial=0.00,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    tempo_dedicato_ore = forms.DecimalField(label="Ore Dedicate (Costo)", initial=0.5, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}))
    data_attivita = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    
    # --- MODIFICA QUI ---
    ruolo = forms.ModelChoiceField(
        label="Eseguita da (Ruolo/Costo)",
        queryset=RuoloCosto.objects.all(), # <-- Punta a RuoloCosto
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # --- FINE MODIFICA ---

    class Meta:
        model = Attivita
        fields = [
            'categoria', 'descrizione', 'prezzo_vendita_attivita',
            'data_attivita', 'tempo_dedicato_ore', 'ruolo' # <-- MODIFICATO (da 'eseguita_da')
        ]

class MessaggioChatForm(forms.ModelForm):
    # ... (invariato) ...
    messaggio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Aggiungi un commento...'}), label=False)
    class Meta:
        model = MessaggioChat
        fields = ['messaggio']

class TrattativaForm(forms.ModelForm):
    # ... (invariato) ...
    titolo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    cliente_nome = forms.CharField(label="Nome Cliente", widget=forms.TextInput(attrs={'class': 'form-control'}))
    cliente_contatto = forms.CharField(label="Email/Telefono Cliente", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    valore_stimato = forms.DecimalField(label="Valore Prodotto Stimato (€)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    commerciale = forms.ModelChoiceField(label="Commerciale Assegnato", queryset=User.objects.filter(is_staff=True), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Trattativa
        fields = ['titolo', 'cliente_nome', 'cliente_contatto', 'valore_stimato', 'commerciale']

class StatMensileForm(forms.ModelForm):
    # ... (invariato) ...
    anno = forms.IntegerField(initial=datetime.date.today().year, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'AAAA'}))
    mese = forms.IntegerField(initial=datetime.date.today().month, min_value=1, max_value=12, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'MM'}))
    costo_marketing_mese = forms.DecimalField(min_value=0, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    costi_operativi_fissi = forms.DecimalField(min_value=0, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    finanziamenti_non_approvati = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = StatMensile 
        fields = ['anno', 'mese', 'costo_marketing_mese', 'costi_operativi_fissi', 'finanziamenti_non_approvati']

class TrattativaDettaglioForm(forms.ModelForm):
    titolo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    cliente_nome = forms.CharField(label="Nome Cliente", widget=forms.TextInput(attrs={'class': 'form-control'}))
    cliente_contatto = forms.CharField(label="Email/Telefono Cliente", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    valore_stimato = forms.DecimalField(label="Valore Prodotto Stimato (€)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    costo_materiali_stimato = forms.DecimalField(label="Costo Materiali Stimato (€)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    commerciale = forms.ModelChoiceField(label="Commerciale Assegnato", queryset=User.objects.filter(is_staff=True), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Trattativa
        fields = ['titolo', 'cliente_nome', 'cliente_contatto', 'valore_stimato', 'costo_materiali_stimato', 'commerciale']