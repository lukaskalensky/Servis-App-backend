from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask import jsonify
from .db import db
from .modely import Moto
from schema.moto import MotoBaseSchema, MotoSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_

blp = Blueprint(
    "moto",
    __name__,
    description="Motorky přihlášeného uživatele",
    url_prefix="/moto"
)


@blp.route("/")
class MotoList(MethodView):

    @jwt_required()
    @blp.response(200, MotoSchema(many=True))
    def get(self):
        """Vrátí motorky aktuálního uživatele"""
        user_id = get_jwt_identity()

        return db.session.execute(
            db.select(Moto).where(Moto.user_id == user_id)
        ).scalars().all()

    @jwt_required()
    @blp.arguments(MotoBaseSchema)
    @blp.response(201, MotoSchema)
    def post(self, moto_data):
        """Vytvoří motorku pro přihlášeného uživatele"""
        user_id = get_jwt_identity()

        moto = Moto(**moto_data, user_id=user_id)

        try:
            db.session.add(moto)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

        return moto


@blp.route("/<int:moto_id>")
class MotoDetail(MethodView):

    @jwt_required()
    @blp.response(200, MotoSchema)
    def get(self, moto_id):
        user_id = get_jwt_identity()

        moto = db.session.execute(
            db.select(Moto).where(
                Moto.id == moto_id,
                Moto.user_id == user_id
            )
        ).scalar_one_or_none()

        if not moto:
            abort(404, message="Motorka nenalezena")

        return moto

    @jwt_required()
    @blp.arguments(MotoBaseSchema)
    @blp.response(200, MotoSchema)
    def put(self, moto_data, moto_id):
        user_id = get_jwt_identity()

        moto = db.session.execute(
            db.select(Moto).where(
                Moto.id == moto_id,
                Moto.user_id == user_id
            )
        ).scalar_one_or_none()

        if not moto:
            abort(404, message="Motorka nenalezena")

        for key, value in moto_data.items():
            setattr(moto, key, value)

        db.session.commit()
        return moto

    @jwt_required()
    def delete(self, moto_id):
        user_id = get_jwt_identity()

        moto = db.session.execute(
            db.select(Moto).where(
                Moto.id == moto_id,
                Moto.user_id == user_id
            )
        ).scalar_one_or_none()

        if not moto:
            abort(404, message="Motorka nenalezena")

        db.session.delete(moto)
        db.session.commit()
        return {"message": "Smazáno"}, 200
