from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    # Administrador CRUDs
    path('colores/', views.ColorListView.as_view(), name='color_list'),
    path('colores/nuevo/', views.ColorCreateView.as_view(), name='color_create'),
    path('colores/<int:pk>/editar/', views.ColorUpdateView.as_view(), name='color_update'),
    path('colores/<int:pk>/eliminar/', views.ColorDeleteView.as_view(), name='color_delete'),

    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),

    path('ropa/', views.RopaListView.as_view(), name='ropa_list'),
    path('ropa/nuevo/', views.RopaCreateView.as_view(), name='ropa_create'),
    path('ropa/<int:pk>/editar/', views.RopaUpdateView.as_view(), name='ropa_update'),
    path('ropa/<int:pk>/eliminar/', views.RopaDeleteView.as_view(), name='ropa_delete'),

    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),

    # Almacenista
    path('catalogo/', views.catalogo_lista, name='catalogo'),
    path('catalogo/<int:id_ropa>/inventario/', views.inventario_editar, name='inventario_editar'),

    # Cajero
    path('ventas/nueva/', views.nueva_venta, name='nueva_venta'),

    # Cajero y Administrador
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/<int:id_venta>/', views.detalle_venta, name='detalle_venta'),
]
