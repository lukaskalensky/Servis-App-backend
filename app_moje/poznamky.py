from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity

from .db import db
from .modely import Poznamky
from app_moje.schema.poznamky import PoznamkySchema, PoznamkyBaseSchema

blp = Blueprint(
    "poznamky",
    __name__,
    description="Operace s poznámkami",
    url_prefix="/poznamky"
)


@blp.route("/")
class PoznamkyList(MethodView):
    @jwt_required()
    @blp.response(200, PoznamkySchema(many=True))
    def get(self):
        user_id = get_jwt_identity()

        return db.session.execute(
            db.select(Poznamky).where(Poznamky.user_id == user_id)
        ).scalars().all()

    @jwt_required()
    @blp.arguments(PoznamkyBaseSchema)
    @blp.response(201, PoznamkySchema)
    def post(self, poznamky_data):
        user_id = get_jwt_identity()
        nova_poznamka = Poznamky(**poznamky_data, user_id=user_id)

        try:
            db.session.add(nova_poznamka)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Chyba databáze: {str(e)}")

        return nova_poznamka


@blp.route("/<int:poznamka_id>")
class PoznamkyDetail(MethodView):

    @jwt_required()
    def delete(self, poznamka_id):
        poznamka = db.session.get(Poznamky, poznamka_id)

        if not poznamka:
            abort(404, message="Poznámka nenalezena")

        db.session.delete(poznamka)
        db.session.commit()

        return {"message": "Smazáno"}, 200
