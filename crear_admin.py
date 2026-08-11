from flask import Flask
from config import Config
from models import db, Administrador
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    usuario = 'valeAdmin'
    password = 'ValeVlim262805'

    if Administrador.query.filter_by(user=usuario).first():
        print('Ese usuario ya existe.')
    else:
        nuevo = Administrador(
            user=usuario,
            password_hash = generate_password_hash(password)
        )
        db.session.add(nuevo)
        db.session.commit()
        print('Administrador creado correctamente.')
    