from marshmallow import Schema, fields, validate


class ServisBaseSchema(Schema):
    nazev_motorky = fields.Str(
        required=True)
    datumdatetime = fields.DateTime(required=True, format="%Y-%m-%d")
    dalsivymenadatetime = fields.DateTime(required=True, format="%Y-%m-%d")
    km = fields.Int(required=True)
    kmdalsi = fields.Int(required=True)
    typ = fields.Str(required=True)
    mnozstvi = fields.Int(required=True)
    poznamky = fields.Str(required=False)
    cena = fields.Int(required=False)
    poloha = fields.Str(required=False)
    imagepocet = fields.Int(required=True)


class ServisSchema(ServisBaseSchema):  # Pro zobrazení dat uživatele (bez hesla)
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
