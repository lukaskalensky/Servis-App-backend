from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import tempfile

import io
import mimetypes
from flask import send_file, request

from .db import db
from .modely import Moto
from .sftp import upload_file_sftp, download_file_sftp

UPLOAD_BASE_PATH = "sftpaplikace/uploads"
UPLOAD_PUBLIC_URL = "sftpaplikace/uploads"

blp = Blueprint(
    "moto_upload",
    __name__,
    description="Upload obrázků motorek",
    url_prefix="/moto"
)


@blp.route("/<string:moto_nazev>/image")
class MotoImageUpload(MethodView):

    @jwt_required()
    def post(self, moto_nazev):
        user_id = get_jwt_identity()

        moto = db.session.execute(
            db.select(Moto).where(
                Moto.nazev == moto_nazev,
                Moto.user_id == user_id
            )
        ).scalar_one_or_none()

        if not moto:
            abort(404, message="Motorka nenalezena")

        if "file" not in request.files:
            abort(400, message="Soubor nebyl přiložen")

        file = request.files["file"]
        if file.filename == "":
            abort(400, message="Prázdný název souboru")

        filename = secure_filename(file.filename)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        remote_path = (
            f"{UPLOAD_BASE_PATH}/moto/{user_id}/{moto_nazev}/{filename}"
        )

        try:
            upload_file_sftp(tmp_path, remote_path)
        finally:
            os.remove(tmp_path)

        moto.image = (
            f"{UPLOAD_PUBLIC_URL}/moto/{user_id}/{moto_nazev}/{filename}"
        )

        db.session.commit()

        return {
            "message": "Obrázek nahrán",
            "image": moto.image
        }, 200

    @jwt_required()
    def get(self, moto_nazev):
        moto = db.session.execute(
            db.select(Moto).where(Moto.nazev == moto_nazev)
        ).scalar_one_or_none()

        if not moto or not moto.image:
            abort(404, message="Motorka nebo obrázek nenalezen")

        filename = os.path.basename(moto.image)

        remote_path = f"{UPLOAD_BASE_PATH}/moto/{moto.user_id}/{moto_nazev}/{filename}"

        try:
            file_bytes = download_file_sftp(remote_path)

            file_stream = io.BytesIO(file_bytes)

            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'image/jpeg'

            return send_file(
                file_stream,
                mimetype=mime_type,
                as_attachment=True,
                download_name=filename
            )

        except FileNotFoundError:
            abort(404, message="Soubor fyzicky chybí na SFTP serveru")
        except Exception as e:
            print(f"Chyba SFTP: {e}")
            abort(500, message="Chyba při stahování souboru")
