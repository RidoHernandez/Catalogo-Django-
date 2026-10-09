from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from io import StringIO
from unittest.mock import patch

from .models import Inventario, Proveedor, Ropa


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
		self.prenda_con_inventario = Ropa.objects.create(
			modelo="Modelo A",
			descripcion="Prenda de prueba",
			tipo="Camisa",
			marca="Marca A",
			precio="250.00",
			proveedor=proveedor,
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
		self.assertContains(response, "Modelo B")
		self.assertContains(response, ">11</td>")
		self.assertContains(response, ">0</td>")
		self.assertContains(
			response,
			f'href="/catalogo/{self.prenda_con_inventario.idRopa}/inventario/"',
		)

	def test_raiz_sigue_mostrando_proveedores(self):
		response = self.client.get("/")

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
			"SecureCajero_239!",
			"SecureCajero_239!",
			"SecureAlmacen_239!",
			"SecureAlmacen_239!",
		],
	)
	def test_crea_usuarios_con_sus_grupos_y_passwords(self, mock_getpass):
		salida = StringIO()
		call_command("crear_usuarios_roles", stdout=salida)

		cajero = User.objects.get(username="cajero")
		almacenista = User.objects.get(username="almacenista")
		self.assertTrue(cajero.check_password("SecureCajero_239!"))
		self.assertTrue(almacenista.check_password("SecureAlmacen_239!"))
		self.assertEqual(list(cajero.groups.values_list("name", flat=True)), ["Cajero"])
		self.assertEqual(
			list(almacenista.groups.values_list("name", flat=True)),
			["Almacenista"],
		)
		self.assertIn("Usuario 'cajero' creado", salida.getvalue())
		self.assertEqual(mock_getpass.call_count, 4)

	def test_ejecucion_repetida_conserva_password_existente(self):
		cajero = User.objects.create_user(username="cajero", password="existing-password")
		User.objects.create_user(username="almacenista", password="existing-password")
		salida = StringIO()

		call_command("crear_usuarios_roles", stdout=salida)

		cajero.refresh_from_db()
		self.assertTrue(cajero.check_password("existing-password"))
		self.assertEqual(list(cajero.groups.values_list("name", flat=True)), ["Cajero"])
		self.assertIn("Usuario 'cajero' actualizado", salida.getvalue())
