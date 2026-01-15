from .db import db
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256 as sha256  # Nebo bcrypt, argon2
from sqlalchemy.orm import foreign
from sqlalchemy import and_


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)

    email = db.Column(db.String(255), nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    motos = db.relationship(
        "Moto",
        back_populates="user",
        cascade="all, delete"
    )

    @property
    def password(self):
        raise AttributeError("Password is write-only")  # getter jen na ochranu

    @password.setter
    def password(self, password):
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        return sha256.verify(password, self.password_hash)


class Moto(db.Model):
    __tablename__ = "motorky"
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(50), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    poznamky = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship("User", back_populates="motos")


class Ukon(db.Model):
    __tablename__ = "ukon"
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(50), nullable=False)
    km = db.Column(db.Integer, nullable=False)
    mesic = db.Column(db.Integer, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship("User", backref="ukony")


class Servis(db.Model):
    __tablename__ = "servis"
    id = db.Column(db.Integer, primary_key=True)
    nazev_motorky = db.Column(db.String(50), nullable=False)
    datumdatetime = db.Column(db.DateTime, nullable=False)
    dalsivymenadatetime = db.Column(db.DateTime, nullable=False)
    km = db.Column(db.Integer, nullable=False)
    kmdalsi = db.Column(db.Integer, nullable=False)
    typ = db.Column(db.String(50), nullable=False)
    mnozstvi = db.Column(db.Integer, nullable=False)
    poznamky = db.Column(db.String(255), nullable=True)
    cena = db.Column(db.Integer, nullable=True)
    poloha = db.Column(db.String(50), nullable=True)
    imagepocet = db.Column(db.Integer, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship("User", backref="servisy")

    # OPRAVA: Přidán primaryjoin, aby se nemíchaly fotky poznámek
    fotky = db.relationship(
        "Fotky",
        primaryjoin="and_(foreign(Fotky.idzaznamu) == Servis.id, Fotky.poznamka_bool == False)",
        back_populates="servis",
        cascade="all, delete-orphan",
        overlaps="poznamky"  # Prevence varování SQLAlchemy
    )


class Fotky(db.Model):
    __tablename__ = "fotky"

    id = db.Column(db.Integer, primary_key=True)
    poznamka_bool = db.Column(db.Boolean, default=False)
    idzaznamu = db.Column(db.Integer, nullable=False)

    pathobrazku = db.Column(db.String(255), nullable=False)

    servis = db.relationship(
        "Servis",
        primaryjoin="and_(foreign(Fotky.idzaznamu) == Servis.id, Fotky.poznamka_bool == False)",
        back_populates="fotky",
        overlaps="poznamky"
    )

    # 2. Relace na POZNÁMKY (platí jen když poznamka_bool == True)
    poznamky = db.relationship(
        "Poznamky",
        primaryjoin="and_(foreign(Fotky.idzaznamu) == Poznamky.id, Fotky.poznamka_bool == True)",
        back_populates="fotky",
        overlaps="servis"
    )


class Tankovani(db.Model):
    __tablename__ = "tankovani"
    id = db.Column(db.Integer, primary_key=True)
    nazev_motorky = db.Column(db.String(50), nullable=False)
    palivo = db.Column(db.String(50), nullable=False)
    datumdatetime = db.Column(db.DateTime, nullable=False)
    km = db.Column(db.Integer, nullable=False)
    mnozstvi = db.Column(db.Integer, nullable=False)
    pumpa = db.Column(db.String(50), nullable=True)
    poznamky = db.Column(db.String(255), nullable=True)
    cena1l = db.Column(db.Integer, nullable=True)
    cenacelkem = db.Column(db.Integer, nullable=True)


class Palivo(db.Model):
    __tablename__ = "palivo"
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(50), nullable=False)


class Poznamky(db.Model):
    __tablename__ = "poznamky"
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(50), nullable=False)
    nazev_motorky = db.Column(db.String(50), nullable=False)
    datumdatetime = db.Column(db.DateTime, nullable=False)
    poznamky = db.Column(db.String(255), nullable=False)
    imagepocet = db.Column(db.Integer, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        overlaps="servis"
    )

    fotky = db.relationship(
        "Fotky",
        # TOTO JE KLÍČOVÁ ÚPRAVA:
        primaryjoin="and_(foreign(Fotky.idzaznamu) == Poznamky.id, Fotky.poznamka_bool == True)",

        # Pokud v modelu Fotky nemáte definovaný vztah zpět k poznámkám,
        # 'back_populates' může dělat problémy.
        # Pokud ho tam máte, nechte ho. Pokud ne, raději použijte viewonly=True pro čtení.
        # Ale pro cascade delete to obvykle potřebujete takto:
        cascade="all, delete-orphan",

        # Důležité pro zamezení chyb při překrývání vztahů
        overlaps="servis"
    )
