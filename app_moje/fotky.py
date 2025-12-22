from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from flask import request
from flask import send_file
import os
import io
import tempfile

from .db import db
from .modely import Servis, Fotky
from schema.fotky import FotkaSchema
from .sftp import upload_file_sftp, download_file_sftp

UPLOAD_BASE_PATH = "/app/uploads"
UPLOAD_PUBLIC_URL = "/app/uploads"

blp = Blueprint(
    "fotky",
    __name__,
    description="Fotky k servisním záznamům",
    url_prefix="/servis"
)


@blp.route("/<int:servis_id>/fotky")
class FotkaUpload(MethodView):

    @jwt_required()
    @blp.response(201, FotkaSchema)
    def post(self, servis_id):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.id == servis_id,
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
            f"user_{user_id}/servis_{servis_id}/{filename}"
        )

        try:
            upload_file_sftp(tmp_path, remote_path)
        finally:
            os.remove(tmp_path)

        fotka = Fotky(
            idzaznamu=servis_id,
            pathobrazku=(
                f"{UPLOAD_PUBLIC_URL}/servis/"
                f"user_{user_id}/servis_{servis_id}/{filename}"
            )
        )

        db.session.add(fotka)
        db.session.commit()

        return fotka


@jwt_required()
@blp.route("/<int:servis_id>/fotky")
class FotkaList(MethodView):

    @blp.response(200, FotkaSchema(many=True))
    def get(self, servis_id):
        user_id = get_jwt_identity()

        servis = db.session.execute(
            db.select(Servis).where(
                Servis.id == servis_id,
                Servis.user_id == user_id
            )
        ).scalar_one_or_none()

        if not servis:
            abort(404, message="Servis nenalezen")

        return servis.fotky


@blp.route("/fotky/<int:fotka_id>/download")
class FotkaDownload(MethodView):

    @jwt_required()
    def get(self, fotka_id):
        user_id = get_jwt_identity()

        fotka = db.session.execute(
            db.select(Fotky)
            .join(Servis)
            .where(
                Fotky.id == fotka_id,
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
            attachment_filename=fotka.pathobrazku.split("/")[-1],
            mimetype="image/jpeg"
        )
