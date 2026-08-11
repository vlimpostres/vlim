use vlim_db;

-- Categorías de productos (Tortas, Kekes, Pack Premium, etc.)

create table categorias (
	id_categorias int auto_increment primary key,
    nombre varchar(50) not null
);

-- Productos generales (sin precio, porque varía por variante)
create table productos (
	id_productos int auto_increment primary key,
    id_categoria int not null,
    nombre varchar(100) not null,
    descripcion text,
    imagen_url varchar(255),
    activo boolean default true,
    foreign key (id_categoria) references categorias(id_categorias)
);

-- Variantes de tamaño/porciones/precio por producto
create table productos_variantes (
	id_prdctV int auto_increment primary key,
    id_producto int not null,
    porciones varchar(50),
    tamano_aprox varchar(100),
    precio decimal(10,2) not null,
    tipo enum('estandar', 'a_pedido') default 'estandar',
    foreign key (id_producto) references productos(id_productos)
);

-- Encabezado de cada venta
create table ventas (
	id_ventas int auto_increment primary key,
    fecha datetime default current_timestamp,
    total decimal(10,2) not null
);

create table detalle_venta(
	id_detalle int auto_increment primary key,
    id_venta int not null,
    id_producto_variante int not null,
    cantidad int not null,
    subtotal decimal(10,2) not null,
    foreign key (id_venta) references ventas(id_ventas),
    foreign key (id_producto_variante) references productos_variantes(id_prdctV)
);

create table administradores (
	id_admin int auto_increment primary key,
    user varchar(50) unique not null,
    password_hash varchar(255) not null 
);
