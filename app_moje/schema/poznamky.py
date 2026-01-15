from marshmallow import Schema, fields, validate


class PoznamkyBaseSchema(Schema):
    nazev = fields.Str(
        required=True)
    nazev_motorky = fields.Str(
        required=True)
    datumdatetime = fields.DateTime(required=True)
    poznamky = fields.Str(required=True)
    imagepocet = fields.Int(required=True)


class PoznamkySchema(PoznamkyBaseSchema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
