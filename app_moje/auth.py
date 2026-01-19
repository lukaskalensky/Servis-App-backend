# backend/app/api/v1/auth.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask import jsonify, current_app
from .db import db
from .modely import User
from app_moje.schema.user import UserRegisterSchema, UserLoginSchema, UserSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from .mail import mail
from flask_mail import Message
import threading


blp = Blueprint("auth", __name__,
                description="Autentizační operace", url_prefix="/auth")


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("Email odeslán do fronty Postfixu.")
        except Exception as e:
            print(f"Chyba při odesílání: {e}")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)
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
        user.password = user_data["password"]

        try:
            db.session.add(user)
            db.session.commit()
            msg = Message("Vítejte v naší aplikaci!",
                          recipients=[user_data["email"]])

            msg.body = f"Dobrý den {user_data['username']},\n\nděkuji za registraci v moji aplikaci."
            real_app = current_app._get_current_object()
            thread = threading.Thread(
                target=send_async_email, args=(real_app, msg))
            thread.start()
        except IntegrityError:
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
        login_identifier = user_data["username_or_email"]
        password = user_data["password"]

        user = db.session.execute(
            db.select(User).where(
                or_(User.username == login_identifier,
                    User.email == login_identifier)
            )
        ).scalar_one_or_none()

        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(
                identity=str(user.id))
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

        abort(401, message="Nesprávné uživatelské jméno/email nebo heslo.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @blp.doc(description="Získá nový přístupový token pomocí platného refresh tokenu.")
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return jsonify(access_token=new_access_token), 200
