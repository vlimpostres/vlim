from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categorias = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id_productos = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categorias'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)    
    variantes = db.relationship('ProductoVariante', backref='producto', lazy=True)

class ProductoVariante(db.Model):
    __tablename__ = 'productos_variantes'
    id_prdctV = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_productos'), nullable=False)
    porciones = db.Column(db.String(50))
    tamano_aprox = db.Column(db.String(100))
    precio = db.Column(db.Numeric(10,2), nullable=False)
    tipo = db.Column(db.Enum('estandar', 'a_pedido'), default='estandar')

class Venta(db.Model):
    __tablename__ = 'ventas'
    id_ventas = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    total = db.Column(db.Numeric(10,2), nullable=False)
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id_ventas'), nullable=False)
    id_producto_variante = db.Column(db.Integer, db.ForeignKey('productos_variantes.id_prdctV'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10,2), nullable=False)
    producto_variante = db.relationship('ProductoVariante')

class Administrador(UserMixin, db.Model):
    __tablename__ = 'administradores'
    id_admin = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id_admin)