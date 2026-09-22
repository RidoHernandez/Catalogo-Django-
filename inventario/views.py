from django.shortcuts import render

from .models import DetalleVenta, Proveedor
from .models import DetalleVenta, Proveedor

# Create your views here.

def lista_detalles_venta(request):
	detalles = DetalleVenta.objects.select_related("venta", "ropa").all()
	return render(
		request,
		"inventario/detalles_venta_lista.html",
		{"detalles": detalles},
	)


def proveedores_lista(request):
	proveedores = Proveedor.objects.all()
	return render(
		request,
		"inventario/proveedores_lista.html",
		{"proveedores": proveedores},
	)
