-- create database inventario;
use inventario;

-- 1. LIMPIEZA DE TABLAS 
SET FOREIGN_KEY_CHECKS = 0; -- Desactivar la validación de llaves foráneas
SET SQL_SAFE_UPDATES = 0;

delete from inventario_detalleventa;
delete from inventario_venta;
delete from inventario_inventario;
delete from inventario_ropa;
delete from inventario_color;
delete from inventario_proveedor;
delete from inventario_cliente;

SET FOREIGN_KEY_CHECKS = 1; -- Reactivar la validación de llaves foráneas
SET SQL_SAFE_UPDATES = 1;

-- Proveedores
INSERT INTO inventario_proveedor (idProveedor, nombre, telefono, direccion) VALUES
(1, 'Textiles Premium S.A.', '555-123-4567', 'Av. Reforma 123, Ciudad de México'),
(2, 'Distribuidora Moda', '555-987-6543', 'Calle 50 #45-20, Zona Centro');

-- Colores
INSERT INTO inventario_color (idColor, descripcion) VALUES
(1, 'Rojo'),
(2, 'Azul Marino'),
(3, 'Negro');

-- Clientes
INSERT INTO inventario_cliente (idCliente, nombre, telefono, correo) VALUES
(1, 'Ana Sofía Rodríguez', '555-1010-202', 'ana.rodriguez@email.com'),
(2, 'Luis Fernando Gómez', '555-3030-404', 'luis.gomez@email.com'),
(3, 'Carmen Valeria Ruiz', '555-5050-606', 'carmen.ruiz@email.com');

-- Ropa
INSERT INTO inventario_ropa (idRopa, modelo, descripcion, tipo, marca, precio, proveedor_id, color_id) VALUES
(1, 'Camiseta Cuello V', 'Camiseta básica de algodón 100%', 'Camiseta', 'Basics', 150.50, 1, 1),
(2, 'Jeans Rectos', 'Pantalón de mezclilla corte recto clásico', 'Pantalón', 'DenimCo', 450.00, 2, 2),
(3, 'Chaqueta de Cuero', 'Chaqueta estilo biker de cuero sintético', 'Chaqueta', 'Urban', 1200.00, 1, 3);


-- Inventario de la ropa
INSERT INTO inventario_inventario (id, talla, unidades, ropa_id) VALUES
(1, 'S', 10, 1),
(2, 'M', 15, 1),
(3, 'L', 5, 1),
(4, '30', 0, 2),
(5, '32', 12, 2),
(6, '34', 8, 2);

-- Ventas 
INSERT INTO inventario_venta (idVenta, fecha, total, cliente_id) VALUES
(1, '2023-11-01', 301.00, 1),
(2, '2023-11-02', 600.50, 2),
(3, '2023-11-03', 900.00, 3);

-- Detalles de Venta 
INSERT INTO inventario_detalleventa (id, cantidad, precioUnitario, subtotal, venta_id, ropa_id) VALUES
(1, 2, 150.50, 301.00, 1, 1),  -- Venta 1: Dos camisetas rojas
(2, 1, 150.50, 150.50, 2, 1),  -- Venta 2: Una camiseta roja...
(3, 1, 450.00, 450.00, 2, 2),  -- Venta 2: ... y unos jeans azules
(4, 2, 450.00, 900.00, 3, 2);  -- Venta 3: Dos jeans azules