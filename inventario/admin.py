from django.contrib import admin
from .models import Cliente, Inventario, Proveedor, Ropa
# Register your models here.

admin.site.register(Proveedor)
admin.site.register(Cliente)
admin.site.register(Ropa)
admin.site.register(Inventario)