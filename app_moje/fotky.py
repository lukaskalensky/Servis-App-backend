from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flask import request
from flask import send_file
import os
import io
import tempfile
from datetime import datetime

from .db import db
from .modely import Servis, Fotky, Poznamky
from app_moje.schema.fotky import FotkaSchema
from .sftp import upload_file_sftp, download_file_sftp

UPLOAD_BASE_PATH = "sftpaplikace/uploads"
UPLOAD_PUBLIC_URL = "sftpaplikace/uploads"

blp = Blueprint(
    "fotky",
    __name__,
    description="Fotky k servisním záznamům",
    url_prefix="/servis"
)


@blp.route("/<int:servis_km>/<string:servis_typ>/fotky")
class FotkaUpload(MethodView):

    @jwt_required()
    @blp.response(201, FotkaSchema)
    def post(self, servis_km, servis_typ):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.km == servis_km,
                Servis.typ == servis_typ,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servis nenalezen nebo nepatří uživateli")

        if "file" not in request.files:
            abort(400, message="Soubor nebyl přiložen")

        file = request.files["file"]
        if file.filename == "":
            abort(400, message="Prázdný soubor")

        filename = secure_filename(file.filename)

        # dočasné uložení
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        remote_path = (
            f"{UPLOAD_BASE_PATH}/servis/"
            f"user_{user_id}/servis_{servis_km}/{filename}"
        )

        try:
            upload_file_sftp(tmp_path, remote_path)
        finally:
            os.remove(tmp_path)

        fotka = Fotky(
            idzaznamu=servis.id,
            pathobrazku=(
                f"{UPLOAD_PUBLIC_URL}/servis/"
                f"user_{user_id}/servis_{servis_km}/{filename}"
            )
        )

        db.session.add(fotka)
        db.session.commit()

        return fotka


@blp.route("/<string:poznamky_datum>/<string:nazev_motorky>/<string:nazev_poznamky>/fotky")
class FotkaPoznamkyUpload(MethodView):

    @jwt_required()
    @blp.response(201, FotkaSchema)
    def post(self, poznamky_datum, nazev_motorky, nazev_poznamky):
        user_id = get_jwt_identity()

        try:
            # Předpokládám formát např. "2023-01-01T12:00:00" - upravte dle formátu frontendu
            dt_object = datetime.fromisoformat(poznamky_datum)
        except ValueError:
            abort(400, message="Neplatný formát data. Očekáván ISO formát.")

        poznamka = db.session.execute(
            db.select(Poznamky).where(
                Poznamky.datumdatetime == dt_object,
                Poznamky.nazev_motorky == nazev_motorky,
                Poznamky.nazev == nazev_poznamky,
                Poznamky.user_id == user_id
            )
        ).scalar_one_or_none()

        if not poznamka:
            abort(404, message="Poznamka nenalezen nebo nepatří uživateli")

        if "file" not in request.files:
            abort(400, message="Soubor nebyl přiložen")

        file = request.files["file"]
        if file.filename == "":
            abort(400, message="Prázdný soubor")

        filename = secure_filename(file.filename)

        # dočasné uložení
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        remote_path = (
            f"{UPLOAD_BASE_PATH}/poznamka/"
            f"user_{user_id}/poznamka_{nazev_poznamky}_{nazev_motorky}/{filename}"
        )

        try:
            upload_file_sftp(tmp_path, remote_path)
        finally:
            os.remove(tmp_path)

        fotka = Fotky(
            idzaznamu=poznamka.id,
            poznamka_bool=True,
            pathobrazku=(
                f"{UPLOAD_BASE_PATH}/poznamka/"
                f"user_{user_id}/poznamka_{nazev_poznamky}_{nazev_motorky}/{filename}"
            )
        )

        db.session.add(fotka)
        db.session.commit()

        return fotka


@blp.route("/<int:servis_km>/<string:servis_typ>/fotky")
class FotkaList(MethodView):

    @jwt_required()
    @blp.response(200, FotkaSchema(many=True))
    def get(self,  servis_km, servis_typ):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.km == servis_km,
                Servis.typ == servis_typ,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servis nenalezen")
        return servis.fotky


@blp.route("/<string:poznamky_datum>/<string:nazev_motorky>/<string:nazev_poznamky>/fotky")
class FotkaPoznamkyList(MethodView):

    @jwt_required()
    @blp.response(200, FotkaSchema(many=True))
    def get(self, poznamky_datum, nazev_motorky, nazev_poznamky):
        user_id = get_jwt_identity()

        try:
            # Předpokládám formát např. "2023-01-01T12:00:00" - upravte dle formátu frontendu
            dt_object = datetime.fromisoformat(poznamky_datum)
        except ValueError:
            abort(400, message="Neplatný formát data. Očekáván ISO formát.")

        poznamka = db.session.execute(
            db.select(Poznamky).where(
                Poznamky.datumdatetime == dt_object,
                Poznamky.nazev_motorky == nazev_motorky,
                Poznamky.nazev == nazev_poznamky,
                Poznamky.user_id == user_id
            )
        ).scalar_one_or_none()

        if not poznamka:
            abort(404, message="Servis nenalezen")
        return db.session.scalars(db.select(Fotky).where(Fotky.idzaznamu == poznamka.id, Fotky.poznamka_bool == True)).all()


@blp.route("/fotky/<int:fotka_id>/download")
class FotkaDownload(MethodView):

    @jwt_required()
    def get(self, fotka_id):
        user_id = get_jwt_identity()

        fotka = db.session.execute(
            db.select(Fotky)
            .join(Fotky.servis)
            .where(
                Fotky.id == fotka_id,
                Fotky.poznamka_bool == False,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not fotka:
            abort(404, message="Fotka nenalezena nebo nepatří uživateli")

        # remote path = cesta uložená v DB
        file_bytes = download_file_sftp(
            fotka.pathobrazku.replace("/static", "/uploads"))

        # streamujeme přes Flask
        return send_file(
            io.BytesIO(file_bytes),
            download_name=fotka.pathobrazku.split(
                "/")[-1],  # Renamed from attachment_filename
            mimetype="image/jpeg",
            as_attachment=True  # Doporučeno přidat, pokud chcete vynutit stažení
        )


@blp.route("/fotky/poznamky/<int:fotka_id>/download")
class FotkaPoznamkyDownload(MethodView):

    @jwt_required()
    def get(self, fotka_id):
        user_id = get_jwt_identity()

        fotka = db.session.execute(
            db.select(Fotky)
            .join(Fotky.poznamky)
            .where(
                Fotky.id == fotka_id,
                Fotky.poznamka_bool == True,
                Poznamky.user_id == user_id
            )
        ).scalar_one_or_none()

        if not fotka:
            abort(404, message="Fotka nenalezena nebo nepatří uživateli")

        # remote path = cesta uložená v DB
        file_bytes = download_file_sftp(
            fotka.pathobrazku.replace("/static", "/uploads"))

        # streamujeme přes Flask
        return send_file(
            io.BytesIO(file_bytes),
            download_name=fotka.pathobrazku.split(
                "/")[-1],  # Renamed from attachment_filename
            mimetype="image/jpeg",
            as_attachment=True  # Doporučeno přidat, pokud chcete vynutit stažení
        )
