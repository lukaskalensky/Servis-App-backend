from marshmallow import Schema, fields, validate


class FotkyBaseSchema(Schema):
    idzaznamu = fields.Int(required=True)
    pathobrazku = fields.Str(required=True)


class FotkaSchema(Schema):
    id = fields.Int(dump_only=True)
    idzaznamu = fields.Int(dump_only=True)
    pathobrazku = fields.Str(dump_only=True)
