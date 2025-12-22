from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from .db import db
from .modely import Servis
from schema.servis import ServisSchema, ServisBaseSchema

blp = Blueprint(
    "servis",
    __name__,
    description="Servisní záznamy",
    url_prefix="/servis"
)


@blp.route("/")
class ServisList(MethodView):

    @jwt_required()
    @blp.response(200, ServisSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()

        return db.session.execute(
            db.select(Servis).where(Servis.user_id == user_id)
        ).scalars().all()

    @jwt_required()
    @blp.arguments(ServisBaseSchema)
    @blp.response(201, ServisSchema)
    def post(self, servis_data):
        user_id = get_jwt_identity()

        servis = Servis(**servis_data, user_id=user_id)

        try:
            db.session.add(servis)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=str(e))

        return servis


@blp.route("/<int:servis_id>")
class ServisDetail(MethodView):

    @jwt_required()
    @blp.response(200, ServisSchema)
    def get(self, servis_id):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.id == servis_id,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servisní záznam nenalezen")

        return servis

    @jwt_required()
    @blp.arguments(ServisBaseSchema)
    @blp.response(200, ServisSchema)
    def put(self, servis_data, servis_id):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.id == servis_id,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servisní záznam nenalezen")

        for key, value in servis_data.items():
            setattr(servis, key, value)

        db.session.commit()
        return servis

    @jwt_required()
    def delete(self, servis_id):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.id == servis_id,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servisní záznam nenalezen")

        db.session.delete(servis)
        db.session.commit()

        return {"message": "Smazáno"}, 200
