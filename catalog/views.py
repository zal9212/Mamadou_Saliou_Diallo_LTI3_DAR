from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from .models import Livre, Emprunt
from django import forms

# Forms
class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'isbn', 'nombre_totaux']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'auteur': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_totaux': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class EmpruntForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = ['livre', 'date_retour']
        widgets = {
            'livre': forms.Select(attrs={'class': 'form-control'}),
            'date_retour': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_livre(self):
        livre = self.cleaned_data.get('livre')
        if livre and not livre.is_available():
            raise forms.ValidationError("Ce livre n'est plus disponible en stock.")
        return livre

# Views
def dashboard(request):
    # Total des exemplaires physiques
    stats_totales = Livre.objects.aggregate(
        total_exemplaires=Sum('nombre_totaux'),
        total_dispos=Sum('nombre_disponibles')
    )
    
    total_exemplaires = stats_totales['total_exemplaires'] or 0
    livres_dispos = stats_totales['total_dispos'] or 0
    livres_empruntes = total_exemplaires - livres_dispos
    
    # Nombre de titres de livres différents
    total_titres = Livre.objects.count()
    
    # Livres en rupture de stock
    rupture_stock = Livre.objects.filter(nombre_disponibles=0).count()
    
    # Auteur avec le plus de titres
    top_auteur_data = Livre.objects.values('auteur').annotate(total=Count('id')).order_by('-total').first()
    top_auteur = top_auteur_data['auteur'] if top_auteur_data else "N/A"
    
    context = {
        'total_exemplaires': total_exemplaires,
        'livres_dispos': livres_dispos,
        'livres_empruntes': livres_empruntes,
        'total_titres': total_titres,
        'rupture_stock': rupture_stock,
        'top_auteur': top_auteur,
    }
    return render(request, 'catalog/dashboard.html', context)

def livre_list(request):
    livres = Livre.objects.all().order_by('titre')
    paginator = Paginator(livres, 3) # 3 par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalog/livre_list.html', {'page_obj': page_obj})

def livre_create(request):
    if request.method == 'POST':
        form = LivreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('livre_list')
    else:
        form = LivreForm()
    return render(request, 'catalog/livre_form.html', {'form': form, 'title': 'Ajouter un Livre'})

def livre_update(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        form = LivreForm(request.POST, instance=livre)
        if form.is_valid():
            form.save()
            return redirect('livre_list')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'catalog/livre_form.html', {'form': form, 'title': 'Modifier un Livre'})

def livre_delete(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        livre.delete()
        return redirect('livre_list')
    return render(request, 'catalog/livre_confirm_delete.html', {'livre': livre})

def emprunt_list(request):
    emprunts = Emprunt.objects.all().order_by('-date_emprunt')
    paginator = Paginator(emprunts, 3) # 3 par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'catalog/emprunt_list.html', {'page_obj': page_obj})

def emprunt_create(request):
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save()
            livre = emprunt.livre
            livre.nombre_disponibles -= 1
            livre.save()
            return redirect('emprunt_list')
    else:
        form = EmpruntForm()
    return render(request, 'catalog/emprunt_form.html', {'form': form, 'title': 'Nouvel Emprunt'})

def emprunt_update(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk)
    if request.method == 'POST':
        form = EmpruntForm(request.POST, instance=emprunt)
        if form.is_valid():
            form.save()
            return redirect('emprunt_list')
    else:
        form = EmpruntForm(instance=emprunt)
    return render(request, 'catalog/emprunt_form.html', {'form': form, 'title': "Modifier l'Emprunt"})

def emprunt_delete(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk)
    if request.method == 'POST':
        # Incrémenter le stock si le livre n'était pas encore rendu
        if not emprunt.date_retour:
            livre = emprunt.livre
            livre.nombre_disponibles += 1
            livre.save()
        emprunt.delete()
        return redirect('emprunt_list')
    return render(request, 'catalog/emprunt_confirm_delete.html', {'emprunt': emprunt})
