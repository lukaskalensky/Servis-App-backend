from marshmallow import Schema, fields, validate


class UkonBaseSchema(Schema):
    nazev = fields.Str(
        required=True)
    km = fields.Int(required=True)
    mesic = fields.Int(required=True)


class UkonSchema(UkonBaseSchema):  # Pro zobrazení dat uživatele (bez hesla)
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
