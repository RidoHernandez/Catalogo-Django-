from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Prefetch
from datetime import date
from django.http import HttpResponseForbidden
from .models import Color, Proveedor, Ropa, Cliente, Inventario, Venta, DetalleVenta
from .permissions import has_role

# Funciones de validación de roles
def is_admin(user):
    return has_role(user, "admin")

def is_almacenista(user):
    return has_role(user, "almacenista")

def is_cajero(user):
    return has_role(user, "cajero")

def is_cajero_or_admin(user):
    return is_cajero(user) or is_admin(user)

# Mixins de roles
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

class CajeroRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_cajero(self.request.user)


class RoleAwareLoginView(LoginView):
    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        if is_admin(self.request.user):
            return reverse_lazy("proveedor_list")
        if is_almacenista(self.request.user):
            return reverse_lazy("catalogo")
        if is_cajero(self.request.user):
            return reverse_lazy("nueva_venta")
        return super().get_success_url()


@login_required
def inicio(request):
    if is_admin(request.user):
        return redirect("proveedor_list")
    if is_almacenista(request.user):
        return redirect("catalogo")
    if is_cajero(request.user):
        return redirect("nueva_venta")
    return HttpResponseForbidden("Tu cuenta todavía no tiene un rol asignado.")

# ========================
# CRUDs (Administrador)
# ========================

class ColorListView(AdminRequiredMixin, ListView):
    model = Color
    template_name = 'inventario/crud_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Colores'
        ctx['nuevo_url'] = 'color_create'
        ctx['editar_url'] = 'color_update'
        ctx['eliminar_url'] = 'color_delete'
        ctx['atributos'] = ['idColor', 'descripcion']
        ctx['indice_filtro'] = 1
        ctx['mostrar_filtro'] = False
        return ctx

class ColorCreateView(AdminRequiredMixin, CreateView):
    model = Color
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('color_list')

class ColorUpdateView(AdminRequiredMixin, UpdateView):
    model = Color
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('color_list')

class ColorDeleteView(AdminRequiredMixin, DeleteView):
    model = Color
    template_name = 'inventario/crud_confirm_delete.html'
    success_url = reverse_lazy('color_list')

class ProveedorListView(AdminRequiredMixin, ListView):
    model = Proveedor
    template_name = 'inventario/crud_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Proveedores'
        ctx['nuevo_url'] = 'proveedor_create'
        ctx['editar_url'] = 'proveedor_update'
        ctx['eliminar_url'] = 'proveedor_delete'
        ctx['atributos'] = ['idProveedor', 'nombre', 'telefono', 'direccion']
        ctx['mostrar_filtro'] = False
        return ctx

class ProveedorCreateView(AdminRequiredMixin, CreateView):
    model = Proveedor
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('proveedor_list')

class ProveedorUpdateView(AdminRequiredMixin, UpdateView):
    model = Proveedor
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('proveedor_list')

class ProveedorDeleteView(AdminRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'inventario/crud_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

class RopaListView(AdminRequiredMixin, ListView):
    model = Ropa
    template_name = 'inventario/crud_list.html'
    context_object_name = 'objetos'
    def get_queryset(self):
        return super().get_queryset().select_related('color')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Ropa'
        ctx['nuevo_url'] = 'ropa_create'
        ctx['editar_url'] = 'ropa_update'
        ctx['eliminar_url'] = 'ropa_delete'
        ctx['atributos'] = ['idRopa', 'modelo', 'tipo', 'marca', 'precio', 'color']
        ctx['indice_filtro'] = 2
        ctx['etiqueta_filtro'] = 'Tipo de prenda'
        ctx['mostrar_filtro'] = True
        return ctx

class RopaCreateView(AdminRequiredMixin, CreateView):
    model = Ropa
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('ropa_list')

class RopaUpdateView(AdminRequiredMixin, UpdateView):
    model = Ropa
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('ropa_list')

class RopaDeleteView(AdminRequiredMixin, DeleteView):
    model = Ropa
    template_name = 'inventario/crud_confirm_delete.html'
    success_url = reverse_lazy('ropa_list')

class ClienteListView(AdminRequiredMixin, ListView):
    model = Cliente
    template_name = 'inventario/crud_list.html'
    context_object_name = 'objetos'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Clientes'
        ctx['nuevo_url'] = 'cliente_create'
        ctx['editar_url'] = 'cliente_update'
        ctx['eliminar_url'] = 'cliente_delete'
        ctx['atributos'] = ['idCliente', 'nombre', 'telefono', 'correo']
        ctx['indice_filtro'] = 1
        ctx['etiqueta_filtro'] = 'Cliente'
        ctx['mostrar_filtro'] = True
        return ctx

class ClienteCreateView(AdminRequiredMixin, CreateView):
    model = Cliente
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteUpdateView(AdminRequiredMixin, UpdateView):
    model = Cliente
    fields = '__all__'
    template_name = 'inventario/crud_form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'inventario/crud_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')

# ========================
# Inventario (Almacenista)
# ========================

from django.views.decorators.http import require_GET

@login_required
@user_passes_test(is_almacenista)
@require_GET
def catalogo_lista(request):
    prendas = Ropa.objects.select_related("proveedor", "color").annotate(
        inventario_total=Coalesce(Sum("inventario__unidades"), 0)
    )
    return render(
        request,
        "inventario/catalogo_lista.html",
        {
            "prendas": prendas,
            "indice_filtro": 2,
            "etiqueta_filtro": "Tipo de prenda",
            "mostrar_filtro": True,
            },
    )

@login_required
@user_passes_test(is_almacenista)
def inventario_editar(request, id_ropa):
    prenda = get_object_or_404(Ropa.objects.select_related("proveedor", "color"), idRopa=id_ropa)
    inventarios = list(Inventario.objects.filter(ropa=prenda).order_by("talla", "id"))
    nueva_talla = ""
    nuevas_unidades = ""
    error_talla = None
    error_unidades = None

    if request.method == "POST":
        valores = {}
        errores = {}
        nueva_talla = request.POST.get("nueva_talla", "").strip()
        nuevas_unidades = request.POST.get("nuevas_unidades", "").strip()

        for inventario in inventarios:
            campo = f"unidades_{inventario.id}"
            valor_capturado = request.POST.get(campo)
            if valor_capturado is None or not str(valor_capturado).strip():
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

        if nueva_talla or nuevas_unidades:
            if not nueva_talla:
                error_talla = "Ingresa una talla para el nuevo inventario."
            elif len(nueva_talla) > 10:
                error_talla = "La talla no puede tener más de 10 caracteres."
            elif any(inv.talla.casefold() == nueva_talla.casefold() for inv in inventarios):
                error_talla = "Esta talla ya existe para la prenda."

            if not nuevas_unidades:
                error_unidades = "Ingresa las unidades de la nueva talla."
            else:
                try:
                    nuevas_unidades = int(nuevas_unidades)
                except ValueError:
                    error_unidades = "Ingresa un número entero válido."
                else:
                    if nuevas_unidades < 0:
                        error_unidades = "Las unidades deben ser mayores o iguales a cero."

        if error_talla:
            errores["nueva_talla"] = error_talla
        if error_unidades:
            errores["nuevas_unidades"] = error_unidades

        if not inventarios and not nueva_talla and not nuevas_unidades:
            error_talla = "Agrega al menos una talla para esta prenda."
            errores["nueva_talla"] = error_talla

        if not errores:
            with transaction.atomic():
                for inventario in inventarios:
                    inventario.unidades = valores[inventario.id]
                    inventario.save(update_fields=["unidades"])
                if nueva_talla:
                    Inventario.objects.create(
                        ropa=prenda,
                        talla=nueva_talla,
                        unidades=nuevas_unidades,
                    )
            messages.success(request, "Inventario actualizado correctamente.")
            return redirect("catalogo")

        filas = [
            {
                "inventario": inv,
                "campo": f"unidades_{inv.id}",
                "valor": request.POST.get(f"unidades_{inv.id}", ""),
                "error": errores.get(f"unidades_{inv.id}"),
            }
            for inv in inventarios
        ]
    else:
        filas = [
            {
                "inventario": inv,
                "campo": f"unidades_{inv.id}",
                "valor": inv.unidades,
                "error": None,
            }
            for inv in inventarios
        ]

    return render(
        request,
        "inventario/inventario_editar.html",
        {
            "prenda": prenda,
            "inventarios": inventarios,
            "filas": filas,
            "nueva_talla": nueva_talla,
            "nuevas_unidades": nuevas_unidades,
            "error_talla": error_talla,
            "error_unidades": error_unidades,
            "errores": errores if request.method == "POST" else {},
        },
    )

# ========================
# Ventas (Cajero y Admin)
# ========================

@login_required
@user_passes_test(is_cajero_or_admin)
def lista_ventas(request):
    ventas = Venta.objects.select_related('cliente').order_by('-fecha', '-idVenta')
    return render(request, 'inventario/lista_ventas.html', {'ventas': ventas})

@login_required
@user_passes_test(is_cajero_or_admin)
def detalle_venta(request, id_venta):
    venta = get_object_or_404(Venta.objects.select_related('cliente'), idVenta=id_venta)
    detalles = DetalleVenta.objects.filter(venta=venta).select_related('ropa__color')
    return render(request, 'inventario/detalle_venta.html', {'venta': venta, 'detalles': detalles})

@login_required
@user_passes_test(is_cajero)
def nueva_venta(request):
    try:
        cliente_default = Cliente.objects.get(nombre='Público general')
    except Cliente.DoesNotExist:
        cliente_default = Cliente.objects.create(nombre='Público general')

    clientes = Cliente.objects.all()
    # Solo mostrar ropa disponible y variantes de talla con existencias positivas.
    ropas = list(
        Ropa.objects.select_related("color")
        .annotate(total_unidades=Coalesce(Sum("inventario__unidades"), 0))
        .filter(total_unidades__gt=0)
        .prefetch_related(
            Prefetch(
                "inventario_set",
                queryset=Inventario.objects.filter(unidades__gt=0).order_by("talla", "id"),
                to_attr="tallas_disponibles",
            )
        )
    )
    productos = {
        str(ropa.idRopa): {
            "nombre": f"{ropa.marca} - {ropa.modelo}",
            "precio": str(ropa.precio),
            "stock_total": ropa.total_unidades,
            "color": ropa.color.descripcion if ropa.color else "Sin color",
            "tallas": [
                {
                    "id": inventario.id,
                    "nombre": inventario.talla,
                    "stock": inventario.unidades,
                }
                for inventario in ropa.tallas_disponibles
            ],
        }
        for ropa in ropas
    }
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos_ids = request.POST.getlist('producto[]')
        inventarios_ids = request.POST.getlist('inventario[]')
        cantidades = request.POST.getlist('cantidad[]')
        
        if not productos_ids or not inventarios_ids or not cantidades:
            messages.error(request, "La venta debe tener al menos un producto.")
            return redirect('nueva_venta')

        errores = []
        if len(productos_ids) != len(inventarios_ids) or len(productos_ids) != len(cantidades):
            errores.append("Los datos de los productos de la venta están incompletos.")
        if len(inventarios_ids) != len(set(inventarios_ids)):
            errores.append("No se puede repetir la misma talla en líneas diferentes.")

        try:
            cliente = Cliente.objects.get(pk=cliente_id)
        except (Cliente.DoesNotExist, ValueError, TypeError):
            cliente = None
            errores.append("Selecciona un cliente válido.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('nueva_venta')

        try:
            lineas = [
                (int(ropa_id), int(inventario_id), int(cantidad))
                for ropa_id, inventario_id, cantidad in zip(
                    productos_ids, inventarios_ids, cantidades
                )
            ]
        except ValueError:
            messages.error(request, "Producto, talla y cantidad deben ser válidos.")
            return redirect("nueva_venta")

        if any(cantidad <= 0 for _, _, cantidad in lineas):
            errores.append("La cantidad de cada producto debe ser mayor a cero.")

        ropa_por_id = Ropa.objects.in_bulk({ropa_id for ropa_id, _, _ in lineas})
        inventario_por_id = {}
        with transaction.atomic():
            inventario_por_id = {
                inventario.id: inventario
                for inventario in Inventario.objects.select_for_update()
                .filter(id__in={inventario_id for _, inventario_id, _ in lineas})
                .select_related("ropa")
            }

            items = []
            total_venta = 0
            for ropa_id, inventario_id, cantidad in lineas:
                ropa = ropa_por_id.get(ropa_id)
                inventario = inventario_por_id.get(inventario_id)
                if ropa is None or inventario is None or inventario.ropa_id != ropa_id:
                    errores.append("Un producto o talla seleccionados no existen.")
                    continue
                if cantidad <= 0:
                    continue
                if inventario.unidades < cantidad:
                    errores.append(
                        f"Stock insuficiente para '{ropa.modelo}' talla "
                        f"{inventario.talla}. Disponible: {inventario.unidades}."
                    )
                    continue
                subtotal = ropa.precio * cantidad
                total_venta += subtotal
                items.append(
                    {
                        "ropa": ropa,
                        "inventario": inventario,
                        "cantidad": cantidad,
                        "precio": ropa.precio,
                        "subtotal": subtotal,
                    }
                )

            if not errores:
                venta = Venta.objects.create(
                    fecha=date.today(),
                    cliente=cliente,
                    total=total_venta,
                )
                for item in items:
                    DetalleVenta.objects.create(
                        venta=venta,
                        ropa=item["ropa"],
                        talla=item["inventario"].talla,
                        cantidad=item["cantidad"],
                        precioUnitario=item["precio"],
                        subtotal=item["subtotal"],
                    )
                    item["inventario"].unidades -= item["cantidad"]
                    item["inventario"].save(update_fields=["unidades"])

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('nueva_venta')
            
        messages.success(request, f"Venta {venta.idVenta} registrada correctamente. Total: ${total_venta}")
        return redirect('lista_ventas')

    return render(request, 'inventario/nueva_venta.html', {
        'clientes': clientes,
        'cliente_default': cliente_default,
        'ropas': ropas,
        'productos_json': productos,
    })
