from django.db import models
# Create your models here.

class Cliente(models.Model):
    idCliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=150)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    idProveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Color(models.Model):
    idColor = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

class Ropa(models.Model):
    idRopa = models.AutoField(primary_key=True)
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    # Relaciones
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.marca} - {self.modelo}"

class Inventario(models.Model):
    # Django agregará un 'id' automáticamente como llave primaria
    unidades = models.IntegerField()
    talla = models.CharField(max_length=10)
    # Relación 1..* con Ropa
    ropa = models.ForeignKey(Ropa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ropa.modelo} - Talla: {self.talla}"

class Venta(models.Model):
    idVenta = models.AutoField(primary_key=True)
    fecha = models.DateField() # O DateTimeField si necesitas la hora exacta
    total = models.DecimalField(max_digits=12, decimal_places=2)
    # Relación *..1 con Cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Venta {self.idVenta} - {self.fecha}"

class DetalleVenta(models.Model):
    cantidad = models.IntegerField()
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    # Relaciones de composición y asociación
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    ropa = models.ForeignKey(Ropa, on_delete=models.PROTECT)

    def __str__(self):
        return f"Detalle de Venta {self.venta.idVenta} - Ropa: {self.ropa.idRopa}"