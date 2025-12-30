from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from .auth import blp as AuthV1Blueprint
from .fotky import blp as FotkyV1Blueprint
from .moto_upload import blp as Moto_UploadV1Blueprint
from .moto import blp as MotoV1Blueprint
from .servis import blp as ServisV1Blueprint
from .ukon import blp as UkonV1Blueprint
from .poznamky import blp as PoznamkyV1Blueprint
from .db import db
from .modely import User, Moto, Servis, Fotky, Ukon, Poznamky


def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lukas:MAUIApp@localhost/MAUIApp'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = "super-secret-default-key-change-me-in-production"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    # Inicializace rozšíření s aplikací
    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

    # Zde můžete přidat další blueprinty (např. pro webové rozhraní, pokud by bylo)
    app.register_blueprint(AuthV1Blueprint)
    app.register_blueprint(FotkyV1Blueprint)
    app.register_blueprint(Moto_UploadV1Blueprint)
    app.register_blueprint(MotoV1Blueprint)
    app.register_blueprint(ServisV1Blueprint)
    app.register_blueprint(UkonV1Blueprint)
    app.register_blueprint(PoznamkyV1Blueprint)
    # Shell kontext pro `flask shell`

    @app.shell_context_processor
    def make_shell_context():
        # Přidejte sem své modely
        return {"db": db, "User": User, "Moto": Moto, "Servis": Servis, "Fotky": Fotky, "Ukon": Ukon, "Poznamky": Poznamky}

    # Jednoduchá testovací routa na kořeni
    @app.route("/hello")
    def hello():
        return "Hello, World from Flask!"

    return app
