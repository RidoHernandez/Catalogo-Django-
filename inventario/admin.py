from django.contrib import admin
from .models import Cliente, Inventario, PerfilUsuario, Proveedor, Ropa
# Register your models here.

admin.site.register(Proveedor)
admin.site.register(Cliente)
admin.site.register(Ropa)
admin.site.register(Inventario)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "telefono", "correo", "usuario_activo")
    list_filter = ("rol", "usuario__is_active")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "usuario__email")
    autocomplete_fields = ("usuario",)

    @admin.display(description="Correo")
    def correo(self, obj):
        return obj.usuario.email

    @admin.display(boolean=True, description="Activo")
    def usuario_activo(self, obj):
        return obj.usuario.is_active