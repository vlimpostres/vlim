class Config:
    SECRET_KEY = 'pon-aqui-tu-clave-secreta'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contraseña@localhost/vlim_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False