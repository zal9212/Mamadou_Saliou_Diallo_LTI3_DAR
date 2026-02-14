from django.db import models

class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    nombre_totaux = models.PositiveIntegerField(default=1)
    nombre_disponibles = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.pk:
            self.nombre_disponibles = self.nombre_totaux
        super().save(*args, **kwargs)

    def is_available(self):
        return self.nombre_disponibles > 0

class Emprunt(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name='emprunts')
    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Emprunt de {self.livre.titre} le {self.date_emprunt}"
