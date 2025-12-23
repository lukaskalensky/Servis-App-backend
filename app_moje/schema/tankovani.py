from marshmallow import Schema, fields, validate


class TankovaniBaseSchema(Schema):
    nazev_motorky = fields.Str(
        required=True)
    palivo = fields.Str(required=True)
    datumdatetime = fields.DateTime(required=True)
    km = fields.Int(required=True)
    mnozstvi = fields.Int(required=True)
    pumpa = fields.Str(required=False)
    poznamky = fields.Str(required=True)
    cena1l = fields.Int(required=False)
    cenacelkem = fields.Int(required=False)


# Pro zobrazení dat uživatele (bez hesla)
class TankovaniSchema(TankovaniBaseSchema):
    id = fields.Int(dump_only=True)
