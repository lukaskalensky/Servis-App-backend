from marshmallow import Schema, fields, validate


class PalivoBaseSchema(Schema):
    nazev = fields.Str(
        required=True)


class PalivoSchema(PalivoBaseSchema):  # Pro zobrazení dat uživatele (bez hesla)
    id = fields.Int(dump_only=True)
