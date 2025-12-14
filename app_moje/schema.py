from marshmallow import Schema, fields, validate


class UserBaseSchema(Schema):
    username = fields.Str(
        required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)


class UserRegisterSchema(UserBaseSchema):
    password = fields.Str(required=True, load_only=True,
                          validate=validate.Length(min=8))
 # Poznámka k politikám pro hesla:
# Pro složitější validaci hesla (např. vyžadování velkých/malých písmen, číslic, speciálních znaků)
# můžete vytvořit vlastní validační funkci nebo použít knihovnu jako `password_strength`.


class UserSchema(UserBaseSchema):  # Pro zobrazení dat uživatele (bez hesla)
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserLoginSchema(Schema):
    # Umožní přihlášení jménem nebo emailem
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
