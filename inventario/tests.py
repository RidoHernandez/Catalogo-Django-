from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from datetime import date
from io import StringIO
from unittest.mock import patch

from .models import (
	Cliente,
	Color,
	DetalleVenta,
	Inventario,
	PerfilUsuario,
	Proveedor,
	Ropa,
	Venta,
)

User = get_user_model()


class CatalogoListaTests(TestCase):
	def setUp(self):
		group_alm, _ = Group.objects.get_or_create(name='Almacenista')
		group_admin, _ = Group.objects.get_or_create(name='Administrador')
		self.user = User.objects.create_user(username='test_almacenista', password='password')
		self.user.groups.add(group_alm, group_admin)
		self.client.login(username='test_almacenista', password='password')
		
		proveedor = Proveedor.objects.create(
			nombre="Proveedor de prueba",
			telefono="5551234567",
			direccion="Calle de prueba",
		)
		color = Color.objects.create(descripcion="Azul")
		self.prenda_con_inventario = Ropa.objects.create(
			modelo="Modelo A",
			descripcion="Prenda de prueba",
			tipo="Camisa",
			marca="Marca A",
			precio="250.00",
			proveedor=proveedor,
			color=color,
		)
		self.prenda_sin_inventario = Ropa.objects.create(
			modelo="Modelo B",
			descripcion="Otra prenda de prueba",
			tipo="Pantalón",
			marca="Marca B",
			precio="450.00",
			proveedor=proveedor,
		)
		Inventario.objects.create(
			ropa=self.prenda_con_inventario,
			talla="M",
			unidades=4,
		)
		Inventario.objects.create(
			ropa=self.prenda_con_inventario,
			talla="L",
			unidades=7,
		)

	def test_catalogo_muestra_prendas_y_suma_inventario(self):
		response = self.client.get("/catalogo/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Modelo A")
		self.assertContains(response, "Azul")
		self.assertContains(response, "Modelo B")
		self.assertContains(response, ">11</td>")
		self.assertContains(response, ">0</td>")
		self.assertContains(
			response,
			f'href="/catalogo/{self.prenda_con_inventario.idRopa}/inventario/"',
		)
		self.assertContains(response, 'id="buscarCatalogo"')
		self.assertContains(response, 'id="filtrarCatalogo"')
		self.assertNotContains(response, 'id="ordenarCatalogo"')

	def test_tabla_de_ropa_muestra_columna_color_y_filtros(self):
		response = self.client.get("/ropa/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "<th>Color</th>")
		self.assertContains(response, "<td>Azul</td>")
		self.assertContains(response, 'id="buscarTabla"')
		self.assertContains(response, 'id="filtrarTabla"')
		self.assertNotContains(response, 'id="ordenarTabla"')

	def test_proveedores_solo_busqueda_sin_combos(self):
		response = self.client.get("/proveedores/")

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="buscarTabla"')
		self.assertNotContains(response, 'id="filtrarTabla"')
		self.assertNotContains(response, 'id="ordenarTabla"')

	def test_tablas_crud_tienen_busqueda_y_filtro_sin_combo_ordenamiento(self):
		for ruta in ("/clientes/",):
			with self.subTest(ruta=ruta):
				response = self.client.get(ruta)

				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'id="buscarTabla"')
				self.assertContains(response, 'id="filtrarTabla"')
				self.assertNotContains(response, 'id="ordenarTabla"')

	def test_historial_y_detalle_usan_ordenamiento_nativo_de_datatables(self):
		cajeros, _ = Group.objects.get_or_create(name="Cajero")
		self.user.groups.set([cajeros])
		venta = Venta.objects.create(
			fecha=date.today(),
			total="250.00",
			cliente=Cliente.objects.get(nombre="Público general"),
		)
		DetalleVenta.objects.create(
			venta=venta,
			ropa=self.prenda_con_inventario,
			talla="M",
			cantidad=1,
			precioUnitario="250.00",
			subtotal="250.00",
		)

		for response in (
			self.client.get("/ventas/"),
			self.client.get(f"/ventas/{venta.idVenta}/"),
		):
			self.assertEqual(response.status_code, 200)
			self.assertNotContains(response, "Ordenar por")

	def test_raiz_sigue_mostrando_proveedores(self):
		response = self.client.get("/", follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Proveedor de prueba")

	def test_catalogo_solo_acepta_get(self):
		response = self.client.post("/catalogo/")

		self.assertEqual(response.status_code, 405)


class InventarioEditarTests(TestCase):
	def setUp(self):
		group, _ = Group.objects.get_or_create(name='Almacenista')
		self.user = User.objects.create_user(username='test_almacenista', password='password')
		self.user.groups.add(group)
		self.client.login(username='test_almacenista', password='password')
		
		self.proveedor = Proveedor.objects.create(
			nombre="Proveedor de prueba",
			telefono="5551234567",
			direccion="Calle de prueba",
		)
		self.prenda = Ropa.objects.create(
			modelo="Modelo de prueba",
			descripcion="Prenda de prueba",
			tipo="Camisa",
			marca="Marca de prueba",
			precio="250.00",
			proveedor=self.proveedor,
		)
		self.inventario_s = Inventario.objects.create(
			ropa=self.prenda,
			talla="S",
			unidades=4,
		)
		self.inventario_m = Inventario.objects.create(
			ropa=self.prenda,
			talla="M",
			unidades=7,
		)
		self.url = f"/catalogo/{self.prenda.idRopa}/inventario/"

	def test_get_muestra_tallas_ordenadas_y_unidades_actuales(self):
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Modelo de prueba")
		self.assertContains(response, f'name="unidades_{self.inventario_s.id}"')
		self.assertContains(response, f'value="{self.inventario_s.unidades}"')
		self.assertLess(
			response.content.index(b">M</td>"),
			response.content.index(b">S</td>"),
		)

	def test_post_valido_actualiza_y_redirige_con_mensaje(self):
		otra_prenda = Ropa.objects.create(
			modelo="Otra prenda",
			descripcion="Prenda externa",
			tipo="Falda",
			marca="Otra marca",
			precio="300.00",
			proveedor=self.proveedor,
		)
		inventario_ajeno = Inventario.objects.create(
			ropa=otra_prenda,
			talla="S",
			unidades=3,
		)
		response = self.client.post(
			self.url,
			{
				f"unidades_{self.inventario_s.id}": "9",
				f"unidades_{self.inventario_m.id}": "12",
				f"unidades_{inventario_ajeno.id}": "500",
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.inventario_s.refresh_from_db()
		self.inventario_m.refresh_from_db()
		inventario_ajeno.refresh_from_db()
		self.assertEqual(self.inventario_s.unidades, 9)
		self.assertEqual(self.inventario_m.unidades, 12)
		self.assertEqual(inventario_ajeno.unidades, 3)
		self.assertContains(response, "Inventario actualizado correctamente.")
		self.assertContains(response, ">21</td>")

	def test_post_invalido_no_guarda_y_conserva_valores_capturados(self):
		for valor, mensaje in (
			("", "Este campo es obligatorio."),
			("-1", "mayores o iguales a cero"),
			("1.5", "número entero válido"),
			("texto", "número entero válido"),
		):
			with self.subTest(valor=valor):
				response = self.client.post(
					self.url,
					{
						f"unidades_{self.inventario_s.id}": "99",
						f"unidades_{self.inventario_m.id}": valor,
					},
				)

				self.assertEqual(response.status_code, 200)
				self.assertContains(response, mensaje)
				self.assertContains(
					response,
					f'value="{valor}"',
				)
				self.inventario_s.refresh_from_db()
				self.inventario_m.refresh_from_db()
				self.assertEqual(self.inventario_s.unidades, 4)
				self.assertEqual(self.inventario_m.unidades, 7)

	def test_post_agrega_talla_y_unidades(self):
		response = self.client.post(
			self.url,
			{
				f"unidades_{self.inventario_s.id}": "4",
				f"unidades_{self.inventario_m.id}": "7",
				"nueva_talla": "XL",
				"nuevas_unidades": "5",
			},
		)

		self.assertRedirects(response, "/catalogo/")
		self.assertTrue(
			Inventario.objects.filter(ropa=self.prenda, talla="XL", unidades=5).exists()
		)
		response = self.client.get(self.url)
		self.assertContains(response, "<td>XL</td>")
		self.assertContains(response, 'value="5"')

	def test_post_no_agrega_talla_duplicada_sin_importar_mayusculas(self):
		response = self.client.post(
			self.url,
			{
				f"unidades_{self.inventario_s.id}": "4",
				f"unidades_{self.inventario_m.id}": "7",
				"nueva_talla": "s",
				"nuevas_unidades": "3",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Esta talla ya existe para la prenda.")
		self.assertEqual(Inventario.objects.filter(ropa=self.prenda).count(), 2)

	def test_prenda_sin_inventario_puede_recibir_su_primera_talla(self):
		prenda = Ropa.objects.create(
			modelo="Primera talla",
			descripcion="Prenda sin stock inicial",
			tipo="Camisa",
			marca="Marca",
			precio="100.00",
			proveedor=self.proveedor,
		)

		response = self.client.post(
			f"/catalogo/{prenda.idRopa}/inventario/",
			{"nueva_talla": "Única", "nuevas_unidades": "2"},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(
			Inventario.objects.filter(ropa=prenda, talla="Única", unidades=2).exists()
		)

	def test_cajero_puede_vender_pero_no_editar_inventario(self):
		cajero, _ = Group.objects.get_or_create(name="Cajero")
		self.user.groups.set([cajero])

		venta_response = self.client.get("/ventas/nueva/")
		inventario_response = self.client.get(self.url)

		self.assertEqual(venta_response.status_code, 200)
		self.assertEqual(inventario_response.status_code, 302)

	def test_almacenista_no_puede_crear_ventas(self):
		response = self.client.get("/ventas/nueva/")

		self.assertEqual(response.status_code, 302)

	def test_menu_muestra_rol_aunque_no_sea_el_primer_grupo(self):
		cajero, _ = Group.objects.get_or_create(name="Cajero")
		self.user.groups.add(cajero)

		response = self.client.get(self.url)

		self.assertContains(response, "Almacén:")
		self.assertContains(response, "Punto de Venta:")

	def test_get_prenda_sin_inventario_no_muestra_guardar(self):
		prenda_sin_inventario = Ropa.objects.create(
			modelo="Sin tallas",
			descripcion="Prenda sin inventario",
			tipo="Accesorio",
			marca="Marca",
			precio="100.00",
			proveedor=self.proveedor,
		)
		response = self.client.get(
			f"/catalogo/{prenda_sin_inventario.idRopa}/inventario/"
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "no tiene registros de inventario")
		self.assertNotContains(response, ">Guardar</button>")

	def test_prenda_inexistente_responde_404(self):
		response = self.client.get("/catalogo/999999/inventario/")

		self.assertEqual(response.status_code, 404)


class CrearUsuariosRolesTests(TestCase):
	@patch(
		"inventario.management.commands.crear_usuarios_roles.getpass",
		side_effect=[
			"SecureAdmin_239!",
			"SecureAdmin_239!",
			"SecureAlmacen_239!",
			"SecureAlmacen_239!",
			"SecureCajero_239!",
			"SecureCajero_239!",
		],
	)
	def test_crea_usuarios_con_sus_grupos_y_passwords(self, mock_getpass):
		salida = StringIO()
		call_command("crear_usuarios_roles", stdout=salida)

		administrador = User.objects.get(username="admin")
		cajero = User.objects.get(username="cajero")
		almacenista = User.objects.get(username="almacenista")
		self.assertTrue(administrador.check_password("SecureAdmin_239!"))
		self.assertTrue(cajero.check_password("SecureCajero_239!"))
		self.assertTrue(almacenista.check_password("SecureAlmacen_239!"))
		self.assertEqual(administrador.perfil.rol, PerfilUsuario.Rol.ADMIN)
		self.assertEqual(list(cajero.groups.values_list("name", flat=True)), ["Cajero"])
		self.assertEqual(
			list(almacenista.groups.values_list("name", flat=True)),
			["Almacenista"],
		)
		self.assertIn("Usuario 'cajero' creado", salida.getvalue())
		self.assertEqual(mock_getpass.call_count, 6)

	def test_ejecucion_repetida_conserva_password_existente(self):
		User.objects.create_user(username="admin", password="existing-password")
		cajero = User.objects.create_user(username="cajero", password="existing-password")
		User.objects.create_user(username="almacenista", password="existing-password")
		salida = StringIO()

		call_command("crear_usuarios_roles", stdout=salida)

		cajero.refresh_from_db()
		self.assertTrue(cajero.check_password("existing-password"))
		self.assertEqual(list(cajero.groups.values_list("name", flat=True)), ["Cajero"])
		self.assertEqual(cajero.perfil.rol, PerfilUsuario.Rol.CAJERO)
		self.assertIn("Usuario 'cajero' actualizado", salida.getvalue())


class PerfilUsuarioTests(TestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(
			username="usuario_rol",
			password="StrongPassword_239!",
			first_name="Usuario",
			last_name="Prueba",
			email="usuario@example.com",
		)

	def test_login_django_acepta_cuenta_con_perfil(self):
		PerfilUsuario.objects.create(
			usuario=self.usuario,
			rol=PerfilUsuario.Rol.CAJERO,
		)

		response = self.client.post(
			"/accounts/login/",
			{"username": "usuario_rol", "password": "StrongPassword_239!"},
		)

		self.assertRedirects(response, "/ventas/nueva/")
		self.assertEqual(int(self.client.session["_auth_user_id"]), self.usuario.pk)

	def test_rol_del_perfil_gobierna_accesos_y_menu(self):
		PerfilUsuario.objects.create(
			usuario=self.usuario,
			rol=PerfilUsuario.Rol.CAJERO,
		)
		almacenistas, _ = Group.objects.get_or_create(name="Almacenista")
		self.usuario.groups.add(almacenistas)
		self.client.login(username="usuario_rol", password="StrongPassword_239!")

		response = self.client.get("/", follow=True)

		self.assertContains(response, "Punto de Venta:")
		self.assertNotContains(response, "Almacén:")
		self.assertEqual(self.client.get("/ventas/nueva/").status_code, 200)
		self.assertEqual(self.client.get("/catalogo/").status_code, 302)


class NuevaVentaPorTallaTests(TestCase):
	def setUp(self):
		cajeros, _ = Group.objects.get_or_create(name="Cajero")
		usuario = User.objects.create_user(username="cajero_venta", password="testpass")
		usuario.groups.add(cajeros)
		self.client.login(username="cajero_venta", password="testpass")
		self.cliente = Cliente.objects.get(nombre="Público general")
		proveedor = Proveedor.objects.create(
			nombre="Proveedor venta",
			telefono="5550000000",
			direccion="Dirección",
		)
		color = Color.objects.create(descripcion="Azul marino")
		self.ropa = Ropa.objects.create(
			modelo="Camisa venta",
			descripcion="Camisa de prueba",
			tipo="Camisa",
			marca="Marca venta",
			precio="250.00",
			proveedor=proveedor,
			color=color,
		)
		self.talla_s = Inventario.objects.create(
			ropa=self.ropa,
			talla="S",
			unidades=3,
		)
		self.talla_m = Inventario.objects.create(
			ropa=self.ropa,
			talla="M",
			unidades=8,
		)
		self.url = "/ventas/nueva/"

	def test_formulario_carga_datos_producto_color_tallas_y_stock(self):
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "productoNombre")
		self.assertContains(response, "productoColor")
		self.assertContains(response, "Azul marino")
		self.assertContains(response, '"stock_total": 11')
		self.assertContains(response, '"nombre": "S"')

	def test_venta_descuenta_talla_seleccionada_y_guarda_talla_en_detalle(self):
		response = self.client.post(
			self.url,
			{
				"cliente": self.cliente.pk,
				"producto[]": [self.ropa.pk],
				"inventario[]": [self.talla_s.pk],
				"cantidad[]": ["2"],
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Venta.objects.count(), 1)
		detalle = DetalleVenta.objects.get()
		self.assertEqual(detalle.talla, "S")
		self.assertEqual(detalle.cantidad, 2)
		self.assertEqual(detalle.subtotal, 500)
		self.talla_s.refresh_from_db()
		self.talla_m.refresh_from_db()
		self.assertEqual(self.talla_s.unidades, 1)
		self.assertEqual(self.talla_m.unidades, 8)

		detalle_response = self.client.get(f"/ventas/{detalle.venta_id}/")
		self.assertContains(detalle_response, "<td>S</td>")
		self.assertContains(detalle_response, "Azul marino")

	def test_no_permite_vender_talla_que_no_pertenece_al_producto(self):
		otra_ropa = Ropa.objects.create(
			modelo="Otra camisa",
			descripcion="Producto distinto",
			tipo="Camisa",
			marca="Otra marca",
			precio="300.00",
			proveedor=self.ropa.proveedor,
		)
		response = self.client.post(
			self.url,
			{
				"cliente": self.cliente.pk,
				"producto[]": [otra_ropa.pk],
				"inventario[]": [self.talla_s.pk],
				"cantidad[]": ["1"],
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Un producto o talla seleccionados no existen.")
		self.assertEqual(Venta.objects.count(), 0)
		self.talla_s.refresh_from_db()
		self.assertEqual(self.talla_s.unidades, 3)

	def test_no_permite_vender_mas_que_stock_de_la_talla(self):
		response = self.client.post(
			self.url,
			{
				"cliente": self.cliente.pk,
				"producto[]": [self.ropa.pk],
				"inventario[]": [self.talla_s.pk],
				"cantidad[]": ["4"],
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Stock insuficiente")
		self.assertEqual(Venta.objects.count(), 0)
		self.talla_s.refresh_from_db()
		self.assertEqual(self.talla_s.unidades, 3)
