# backend/app/api/v1/auth.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask import jsonify
from .db import db
from .modely import User
from app_moje.schema.user import UserRegisterSchema, UserLoginSchema, UserSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_  # Pro vyhledávání podle jména NEBO emailu

# Vytvoření nového blueprintu pro autentizaci
blp = Blueprint("auth", __name__,
                description="Autentizační operace", url_prefix="/auth")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)  # Vrátíme data nového uživatele (bez hesla)
    def post(self, user_data):
        """Registruje nového uživatele."""
        if db.session.execute(db.select(User).where(User.username == user_data["username"])).scalar_one_or_none():
            abort(409, message="Uživatel s tímto jménem již existuje.")
        if db.session.execute(db.select(User).where(User.email == user_data["email"])).scalar_one_or_none():
            abort(409, message="Uživatel s tímto emailem již existuje.")

        user = User(
            username=user_data["username"],
            email=user_data["email"]
        )
        user.password = user_data["password"]  # Nastaví hash hesla

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:  # Pro případ, že by unikátnost selhala na úrovni DB
            db.session.rollback()
            abort(500, message="Chyba při ukládání uživatele.")
        except Exception as e:
            db.session.rollback()
            abort(500, message=str(e))
        return user


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Přihlásí uživatele a vrátí JWT tokeny."""
        login_identifier = user_data["username_or_email"]
        password = user_data["password"]

        user = db.session.execute(
            db.select(User).where(
                or_(User.username == login_identifier,
                    User.email == login_identifier)
            )
        ).scalar_one_or_none()

        if user and user.check_password(password):
            # Identita pro JWT může být ID uživatele
            access_token = create_access_token(str(identity=user.id))
            refresh_token = create_refresh_token(
                str(identity=user.id))  # Volitelný refresh token
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

        abort(401, message="Nesprávné uživatelské jméno/email nebo heslo.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @blp.doc(description="Získá nový přístupový token pomocí platného refresh tokenu.")
    # Vyžaduje platný refresh token v Authorization hlavičce
    @jwt_required(refresh=True)
    def post(self):
        # Získá identitu uživatele z refresh tokenu
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=str(current_user_id))
        return jsonify(access_token=new_access_token), 200
