from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from datetime import date
from .models import Color, Proveedor, Ropa, Cliente, Inventario, Venta, DetalleVenta

# Funciones de validación de roles
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Administrador').exists()

def is_almacenista(user):
    return user.is_superuser or user.groups.filter(name='Almacenista').exists()

def is_cajero(user):
    return user.is_superuser or user.groups.filter(name='Cajero').exists()

def is_cajero_or_admin(user):
    return user.is_superuser or user.groups.filter(name__in=['Cajero', 'Administrador']).exists()

# Mixins de roles
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

class CajeroRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_cajero(self.request.user)

@login_required
def inicio(request):
    return render(request, 'base.html')

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
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Ropa'
        ctx['nuevo_url'] = 'ropa_create'
        ctx['editar_url'] = 'ropa_update'
        ctx['eliminar_url'] = 'ropa_delete'
        ctx['atributos'] = ['idRopa', 'modelo', 'tipo', 'marca', 'precio']
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
    return render(request, "inventario/catalogo_lista.html", {"prendas": prendas})

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
    # Solo ropa que tenga inventario disponible
    ropas = Ropa.objects.annotate(total_unidades=Coalesce(Sum('inventario__unidades'), 0)).filter(total_unidades__gt=0)
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        productos_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')
        
        if not productos_ids or not cantidades:
            messages.error(request, "La venta debe tener al menos un producto.")
            return redirect('nueva_venta')
            
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        # Validaciones
        errores = []
        if len(productos_ids) != len(set(productos_ids)):
            errores.append("No se puede agregar el mismo producto dos veces en líneas diferentes.")
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('nueva_venta')

        try:
            with transaction.atomic():
                items = []
                total_venta = 0
                
                for p_id, cant in zip(productos_ids, cantidades):
                    try:
                        cant_int = int(cant)
                    except ValueError:
                        errores.append(f"Cantidad inválida para producto ID {p_id}.")
                        continue
                        
                    ropa = get_object_or_404(Ropa, idRopa=p_id)
                    
                    if cant_int <= 0:
                        errores.append(f"La cantidad para '{ropa.modelo}' debe ser mayor a 0.")
                        continue
                        
                    inventarios = list(Inventario.objects.select_for_update().filter(ropa=ropa, unidades__gt=0).order_by('id'))
                    total_disponible = sum(inv.unidades for inv in inventarios)
                    
                    if cant_int > total_disponible:
                        errores.append(f"Stock insuficiente para '{ropa.modelo}'. Solicitado: {cant_int}, Disponible: {total_disponible}.")
                        continue
                    
                    subtotal = ropa.precio * cant_int
                    total_venta += subtotal
                    items.append({'ropa': ropa, 'cantidad': cant_int, 'precio': ropa.precio, 'subtotal': subtotal, 'inventarios': inventarios})

                if errores:
                    raise ValueError("Validation error")
                    
                venta = Venta.objects.create(fecha=date.today(), cliente=cliente, total=total_venta)
                for item in items:
                    DetalleVenta.objects.create(
                        venta=venta,
                        ropa=item['ropa'],
                        cantidad=item['cantidad'],
                        precioUnitario=item['precio'],
                        subtotal=item['subtotal']
                    )
                    
                    cant_restante = item['cantidad']
                    for inv in item['inventarios']:
                        if cant_restante == 0:
                            break
                        if inv.unidades >= cant_restante:
                            inv.unidades -= cant_restante
                            inv.save(update_fields=['unidades'])
                            cant_restante = 0
                        else:
                            cant_restante -= inv.unidades
                            inv.unidades = 0
                            inv.save(update_fields=['unidades'])
        except ValueError:
            pass
            
        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('nueva_venta')
            
        messages.success(request, f"Venta {venta.idVenta} registrada correctamente. Total: ${total_venta}")
        return redirect('lista_ventas')

    return render(request, 'inventario/nueva_venta.html', {
        'clientes': clientes,
        'cliente_default': cliente_default,
        'ropas': ropas
    })
