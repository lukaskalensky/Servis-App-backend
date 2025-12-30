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

    @jwt_required()
    def get(self, moto_id):
        # 1. Najdeme záznam v databázi
        moto = db.session.execute(
            db.select(Moto).where(Moto.id == moto_id)
        ).scalar_one_or_none()

        if not moto or not moto.image:
            abort(404, message="Motorka nebo obrázek nenalezen")

        # 2. Rekonstrukce cesty k souboru na SFTP
        # V databázi máte uloženou URL (např. .../filename.jpg), musíme z ní získat název souboru
        filename = os.path.basename(moto.image)

        # Sestavíme cestu, kde by měl soubor na SFTP ležet
        # Musí to odpovídat logice, kterou jste použil při uploadu:
        # f"{UPLOAD_BASE_PATH}/moto/{user_id}/{moto_id}/{filename}"
        remote_path = f"{UPLOAD_BASE_PATH}/moto/{moto.user_id}/{moto_id}/{filename}"

        try:
            # 3. Stažení bytů přes vaši SFTP funkci
            file_bytes = download_file_sftp(remote_path)

            # 4. Příprava odpovědi
            # Převedeme bytes na stream, kterému Flask rozumí
            file_stream = io.BytesIO(file_bytes)

            # Zkusíme odhadnout typ souboru (image/jpeg, image/png) podle přípony
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'image/jpeg'  # Fallback

            return send_file(
                file_stream,
                mimetype=mime_type,
                as_attachment=True,  # False = zobrazit v prohlížeči/appce, True = stáhnout
                download_name=filename
            )

        except FileNotFoundError:
            abort(404, message="Soubor fyzicky chybí na SFTP serveru")
        except Exception as e:
            # Logování chyby
            print(f"Chyba SFTP: {e}")
            abort(500, message="Chyba při stahování souboru")
