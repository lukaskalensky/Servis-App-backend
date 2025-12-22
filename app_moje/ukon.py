from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from .db import db
from .modely import Ukon
from app_moje.schema.ukon import UkonSchema, UkonBaseSchema

blp = Blueprint(
    "ukon",
    __name__,
    description="Úkony přihlášeného uživatele",
    url_prefix="/ukon"
)


@blp.route("/")
class UkonList(MethodView):

    @jwt_required()
    @blp.response(200, UkonSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()

        return db.session.execute(
            db.select(Ukon).where(Ukon.user_id == user_id)
        ).scalars().all()

    @jwt_required()
    @blp.arguments(UkonBaseSchema)
    @blp.response(201, UkonSchema)
    def post(self, ukon_data):
        user_id = get_jwt_identity()

        ukon = Ukon(**ukon_data, user_id=user_id)

        try:
            db.session.add(ukon)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

        return ukon


@blp.route("/<int:ukon_id>")
class UkonDetail(MethodView):

    @jwt_required()
    @blp.response(200, UkonSchema)
    def get(self, ukon_id):
        user_id = get_jwt_identity()

        ukon = db.session.execute(
            db.select(Ukon).where(
                Ukon.id == ukon_id,
                Ukon.user_id == user_id
            )
        ).scalar_one_or_none()

        if not ukon:
            abort(404, message="Úkon nenalezen")

        return ukon

    @jwt_required()
    @blp.arguments(UkonBaseSchema)
    @blp.response(200, UkonSchema)
    def put(self, ukon_data, ukon_id):
        user_id = get_jwt_identity()

        ukon = db.session.execute(
            db.select(Ukon).where(
                Ukon.id == ukon_id,
                Ukon.user_id == user_id
            )
        ).scalar_one_or_none()

        if not ukon:
            abort(404, message="Úkon nenalezen")

        for key, value in ukon_data.items():
            setattr(ukon, key, value)

        db.session.commit()
        return ukon

    @jwt_required()
    def delete(self, ukon_id):
        user_id = get_jwt_identity()

        ukon = db.session.execute(
            db.select(Ukon).where(
                Ukon.id == ukon_id,
                Ukon.user_id == user_id
            )
        ).scalar_one_or_none()

        if not ukon:
            abort(404, message="Úkon nenalezen")

        db.session.delete(ukon)
        db.session.commit()

        return {"message": "Smazáno"}, 200
