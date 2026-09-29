from django.test import TestCase

from .models import Inventario, Proveedor, Ropa


class CatalogoListaTests(TestCase):
	def setUp(self):
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
