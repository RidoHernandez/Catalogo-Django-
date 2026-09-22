from django.shortcuts import render

from .models import DetalleVenta, Proveedor

# Create your views here.


def lista_detalles_venta(request):
	detalles = DetalleVenta.objects.select_related("venta", "ropa").all()
	return render(
		request,
		"inventario/detalles_venta_lista.html",
		{"detalles": detalles},
	)

def Proveedor_lista(request):
	proveedores = Proveedor.objects.all()
	return render(
		request,
		"inventario/Proveedor_lista.html",
		{"proveedores": proveedores},
	)
