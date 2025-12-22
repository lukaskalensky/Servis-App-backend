from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import tempfile

from .db import db
from .modely import Moto
from .sftp import upload_file_sftp

UPLOAD_BASE_PATH = "/app/uploads"
UPLOAD_PUBLIC_URL = "/app/uploads"

blp = Blueprint(
    "moto_upload",
    __name__,
    description="Upload obrázků motorek",
    url_prefix="/moto"
)


@blp.route("/<int:moto_id>/image")
class MotoImageUpload(MethodView):

    @jwt_required()
    def post(self, moto_id):
        user_id = get_jwt_identity()

        moto = db.session.execute(
            db.select(Moto).where(
                Moto.id == moto_id,
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

        # dočasné uložení
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        remote_path = (
            f"{UPLOAD_BASE_PATH}/moto/{user_id}/{moto_id}/{filename}"
        )

        try:
            upload_file_sftp(tmp_path, remote_path)
        finally:
            os.remove(tmp_path)

        moto.image = (
            f"{UPLOAD_PUBLIC_URL}/moto/{user_id}/{moto_id}/{filename}"
        )

        db.session.commit()

        return {
            "message": "Obrázek nahrán",
            "image": moto.image
        }, 200
