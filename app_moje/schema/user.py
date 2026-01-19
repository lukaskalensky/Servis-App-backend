from marshmallow import Schema, fields, validate


class UserBaseSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)


class UserRegisterSchema(UserBaseSchema):
    password = fields.Str(required=True, load_only=True,
                          validate=validate.Length(min=8))


class UserSchema(UserBaseSchema):
    id = fields.Int(dump_only=True)


class UserLoginSchema(Schema):
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
