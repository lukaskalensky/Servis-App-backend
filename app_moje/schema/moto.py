from marshmallow import Schema, fields, validate


class MotoBaseSchema(Schema):
    nazev = fields.Str(
        required=True)
    km = fields.Int(required=True)
    poznamky = fields.Str(required=False)
    image = fields.Str(required=False)


class MotoSchema(MotoBaseSchema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
