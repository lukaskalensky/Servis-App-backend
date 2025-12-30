from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from modely import Poznamky  # Ujisti se, že importuješ model správně
from schema.poznamky import PoznamkySchema, PoznamkyBaseSchema

blp = Blueprint(
    "poznamky",
    __name__,
    description="Operace s poznámkami",
    url_prefix="/poznamky"
)


@blp.route("/")
class PoznamkyList(MethodView):

    # --- GET: Získání všech poznámek ---
    @jwt_required()
    @blp.response(200, PoznamkySchema(many=True))
    def get(self):
        # Pokud bys měl v modelu user_id, filtroval bys takto:
        # user_id = get_jwt_identity()
        # return db.session.execute(db.select(Poznamky).where(Poznamky.user_id == user_id)).scalars().all()

        # Bez user_id vracíme vše:
        return db.session.execute(
            db.select(Poznamky)
        ).scalars().all()

    # --- POST: Přidání nové poznámky ---
    @jwt_required()
    @blp.arguments(PoznamkyBaseSchema)
    @blp.response(201, PoznamkySchema)
    def post(self, poznamky_data):
        # Vytvoření instance modelu
        nova_poznamka = Poznamky(**poznamky_data)

        try:
            db.session.add(nova_poznamka)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Chyba databáze: {str(e)}")

        return nova_poznamka


@blp.route("/<int:poznamka_id>")
class PoznamkyDetail(MethodView):

    # --- DELETE: Smazání poznámky (pro úplnost) ---
    @jwt_required()
    def delete(self, poznamka_id):
        poznamka = db.session.get(Poznamky, poznamka_id)

        if not poznamka:
            abort(404, message="Poznámka nenalezena")

        db.session.delete(poznamka)
        db.session.commit()

        return {"message": "Smazáno"}, 200
