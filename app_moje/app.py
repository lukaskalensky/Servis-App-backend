# from .auth import blp as AuthV1Blueprint
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from datetime import timedelta

# app = Flask(__name__)
# app.register_blueprint(AuthV1Blueprint)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lukas:MAUIApp@localhost/MAUIApp'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["JWT_SECRET_KEY"] = "super-secret-default-key-change-me-in-production"
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


# db = SQLAlchemy(app)
# db.init_app(app)
# jwt = JWTManager(app)

# --- Inicializace databáze ---
# with app.app_context():
#    db.create_all()


# @app.route("/")
# def hello():
#    return "Flask běží přes Apache"
