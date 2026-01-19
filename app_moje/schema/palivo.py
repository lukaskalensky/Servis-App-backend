from marshmallow import Schema, fields, validate


class PalivoBaseSchema(Schema):
    nazev = fields.Str(
        required=True)


class PalivoSchema(PalivoBaseSchema):
    id = fields.Int(dump_only=True)
