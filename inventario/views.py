from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .models import DetalleVenta, Inventario, Proveedor, Ropa

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


@require_GET
def catalogo_lista(request):
	prendas = Ropa.objects.select_related("proveedor", "color").annotate(
		inventario_total=Coalesce(Sum("inventario__unidades"), 0)
	)
	return render(
		request,
		"inventario/catalogo_lista.html",
		{"prendas": prendas},
	)


@require_http_methods(["GET", "POST"])
def inventario_editar(request, id_ropa):
	prenda = get_object_or_404(
		Ropa.objects.select_related("proveedor", "color"),
		idRopa=id_ropa,
	)
	inventarios = list(
		Inventario.objects.filter(ropa=prenda).order_by("talla", "id")
	)

	if request.method == "POST":
		valores = {}
		errores = {}
		for inventario in inventarios:
			campo = f"unidades_{inventario.id}"
			valor_capturado = request.POST.get(campo)
			if valor_capturado is None or not valor_capturado.strip():
				errores[campo] = "Este campo es obligatorio."
				continue

			try:
				unidades = int(valor_capturado)
			except ValueError:
				errores[campo] = "Ingresa un número entero válido."
				continue

			if unidades < 0:
				errores[campo] = "Las unidades deben ser mayores o iguales a cero."
				continue

			valores[inventario.id] = unidades

		if not errores:
			with transaction.atomic():
				for inventario in inventarios:
					inventario.unidades = valores[inventario.id]
					inventario.save(update_fields=["unidades"])
			messages.success(request, "Inventario actualizado correctamente.")
			return redirect("catalogo")

		filas = [
			{
				"inventario": inventario,
				"campo": f"unidades_{inventario.id}",
				"valor": request.POST.get(
					f"unidades_{inventario.id}", ""
				),
				"error": errores.get(f"unidades_{inventario.id}"),
			}
			for inventario in inventarios
		]
	else:
		filas = [
			{
				"inventario": inventario,
				"campo": f"unidades_{inventario.id}",
				"valor": inventario.unidades,
				"error": None,
			}
			for inventario in inventarios
		]

	return render(
		request,
		"inventario/inventario_editar.html",
		{"prenda": prenda, "inventarios": inventarios, "filas": filas},
	)
