from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import os
from config import Config
from models import db, Categoria, Producto, Administrador, ProductoVariante, Venta, DetalleVenta
from sqlalchemy import func
from datetime import datetime
import cloudinary
import cloudinary.uploader


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET'],
    secure=True
)


@login_manager.user_loader
def load_user(id_admin):
   return db.session.get(Administrador, int(id_admin))

@app.route('/')
def home():
    categorias = Categoria.query.all()
    return render_template('landing.html', categorias=categorias)

@app.route('/api/producto/<int:id>')
def api_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'imagen_url': producto.imagen_url,
        'variantes': [
            {
                'porciones': v.porciones,
                'tamano': v.tamano_aprox,
                'precio': float(v.precio),
                'tipo': v.tipo
            } for v in producto.variantes
        ]
    })

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        admin = Administrador.query.filter_by(user=usuario).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Usuario o contraseña incorrecta.')
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    productos = Producto.query.order_by(Producto.id_productos.desc()).limit(5).all()
    ventas = Venta.query.order_by(Venta.fecha.desc()).limit(5).all()

    total_transacciones = Venta.query.count()
    total_unidades = db.session.query(func.sum(DetalleVenta.cantidad)).scalar() or 0
    ingresos_totales = db.session.query(func.sum(Venta.total)).scalar() or 0

    mes_actual = datetime.now().strftime('%Y-%m')
    ingreso_mes_actual = db.session.query(func.sum(Venta.total)).filter(
        func.date_format(Venta.fecha, '%Y-%m') == mes_actual
    ).scalar() or 0

    return render_template('admin/dashboard.html',
        productos=productos, ventas=ventas,
        total_transacciones=total_transacciones, total_unidades=total_unidades,
        ingresos_totales=ingresos_totales, ingreso_mes_actual=ingreso_mes_actual
    )

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin/producto/<int:id>')
@login_required
def admin_producto_detalle(id):
    producto = Producto.query.get_or_404(id)
    return render_template('admin/producto_detalle.html', producto=producto)

@app.route('/admin/producto/<int:id>/variante/nueva', methods=['POST'])
@login_required
def admin_variante_nueva(id):
    producto = Producto.query.get_or_404(id)

    nueva_variante = ProductoVariante(
        id_producto=producto.id_productos,
        porciones=request.form['porciones'],
        tamano_aprox=request.form['tamano_aprox'],
        precio=request.form['precio'],
        tipo=request.form['tipo']
    )
    db.session.add(nueva_variante)
    db.session.commit()

    return redirect(url_for('admin_producto_detalle', id=id))

@app.route('/admin/producto/nuevo', methods=['GET', 'POST'])
@app.route('/admin/producto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_producto_form(id=None):
    categorias = Categoria.query.all()
    producto = Producto.query.get(id) if id else None

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        id_categoria = request.form['id_categoria']

        imagen_url = producto.imagen_url if producto else None
        archivo = request.files.get('imagen')
        if archivo and archivo.filename != '':
            resultado = cloudinary.uploader.upload(archivo)
            imagen_url = resultado['secure_url']

        if producto:
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.id_categoria = id_categoria
            producto.imagen_url = imagen_url
        else:
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                id_categoria=id_categoria,
                imagen_url=imagen_url,
                activo=True
            )
            db.session.add(producto)

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/producto_form.html', categorias=categorias, producto=producto)

@app.route('/admin/producto/<int:id>/eliminar', methods=['POST'])
@login_required
def admin_producto_eliminar(id):
    producto = Producto.query.get_or_404(id)
    producto.activo = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/producto/<int:id>/activar', methods=['POST'])
@login_required
def admin_producto_activar(id):
    producto = Producto.query.get_or_404(id)
    producto.activo = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/productos')
@login_required
def admin_productos_lista():
    productos = Producto.query.all()
    return render_template('admin/productos_lista.html', productos=productos)

@app.route('/admin/ventas')
@login_required
def admin_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('admin/ventas.html', ventas=ventas)

@app.route('/admin/ventas/nueva', methods=['GET', 'POST'])
@login_required
def admin_venta_nueva():
    if request.method == 'POST':
        variante_ids = request.form.getlist('variante_id[]')
        cantidades = request.form.getlist('cantidad[]')

        total = 0
        nueva_venta = Venta(total=0)
        db.session.add(nueva_venta)
        db.session.flush()

        for vid, cant in zip(variante_ids, cantidades):
            if not vid or not cant:
                continue
            variante = ProductoVariante.query.get(int(vid))
            cantidad = int(cant)
            subtotal = float(variante.precio) * cantidad

            detalle = DetalleVenta(
                id_venta = nueva_venta.id_ventas,
                id_producto_variante = variante.id_prdctV,
                cantidad = cantidad,
                subtotal = subtotal
            )
            db.session.add(detalle)
            total += subtotal

        nueva_venta.total = total
        db.session.commit()

        return redirect(url_for('admin_ventas'))

    productos = Producto.query.filter_by(activo=True).all()
    return render_template('admin/venta_form.html', productos=productos)

@app.route('/api/reportes/mas-vendidos')
@login_required
def api_mas_vendidos():
    resultados = db.session.query(
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(ProductoVariante, DetalleVenta.id_producto_variante == ProductoVariante.id_prdctV
    ).join(Producto, ProductoVariante.id_producto == Producto.id_productos
    ).group_by(Producto.nombre
    ).order_by(func.sum(DetalleVenta.cantidad).desc()
    ).limit(5).all()

    return jsonify({
        'labels': [r.nombre for r in resultados],
        'valores': [int(r.total_vendido) for r in resultados]
    })

@app.route('/api/reportes/ingresos-por-mes')
@login_required
def api_ingresos_por_mes():
    resultados = db.session.query(
        func.date_format(Venta.fecha, '%Y-%m').label('mes'),
        func.sum(Venta.total).label('total')
    ).group_by('mes').order_by('mes').all()

    return jsonify({
        'labels': [r.mes for r in resultados],
        'valores': [float(r.total) for r in resultados]
    })

@app.route('/api/reportes/ingresos-por-categoria')
@login_required
def api_ingresos_por_categoria():
    resultados = db.session.query(
        Categoria.nombre,
        func.sum(DetalleVenta.cantidad).label('cantidad'),
        func.sum(DetalleVenta.subtotal).label('ingreso')
    ).join(Producto, Categoria.id_categorias == Producto.id_categoria
    ).join(ProductoVariante, Producto.id_productos == ProductoVariante.id_producto
    ).join(DetalleVenta, ProductoVariante.id_prdctV == DetalleVenta.id_producto_variante
    ).group_by(Categoria.nombre
    ).order_by(func.sum(DetalleVenta.cantidad).desc()
    ).all()

    return jsonify({
        'labels': [r.nombre for r in resultados],
        'cantidades': [int(r.cantidad) for r in resultados],
        'ingresos': [float(r.ingreso) for r in resultados]
    })

@app.route('/terminos')
def terminos():
    return render_template('terminos.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')