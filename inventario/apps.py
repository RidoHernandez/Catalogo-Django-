from django.apps import AppConfig
from django.db.models.signals import post_migrate

def inicializar_datos(sender, **kwargs):
    from django.contrib.auth.models import Group
    from .models import Cliente
    Group.objects.get_or_create(name='Administrador')
    Group.objects.get_or_create(name='Almacenista')
    Group.objects.get_or_create(name='Cajero')
    Cliente.objects.get_or_create(nombre='Público general', defaults={'telefono': '', 'correo': ''})

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
        post_migrate.connect(inicializar_datos, sender=self)
