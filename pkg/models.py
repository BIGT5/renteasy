from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__= "admin_table"

    admin_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_username= db.Column(db.String(100),nullable=False,unique=True)
    password= db.Column(db.String(200),nullable=False)
    last_login= db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.admin_id}'

class Chat(db.Model):
    __tablename__= "chat_table"

    chat_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    chat_text = db.Column(db.Text,nullable=False)
    landlord_id = db.Column(db.ForeignKey("landlord_details.landlord_id",ondelete="CASCADE"), nullable=False)
    tenant_id = db.Column(db.ForeignKey("tenant_details.tenant_id",ondelete="CASCADE"), nullable=False)
    message_time = db.Column(db.DateTime, default=datetime.utcnow)

    landlord = db.relationship("Landlord", backref=db.backref("chatdeets",cascade="all, delete"))
    tenant = db.relationship("Tenant", backref="chatdeets")

    def __str__(self):
        return f'{self.chat_id}'

class Pictures(db.Model):
    __tablename__= "house_pictures_table"

    picture_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    pictures = db.Column(db.String(200),nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("vacant_houses.house_id", ondelete="CASCADE"))

    def __str__(self):
        return f"{self.picture_id}"

class Types(db.Model):
    __tablename__= "house_type"

    house_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    type_name = db.Column(db.String(100),nullable=False,unique=True)

    vacant = db.relationship("Vacant", backref="house_type")

    def __str__(self):
        return f'{self.house_id}'

class Landlord(db.Model):
    __tablename__= "landlord_details"

    landlord_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    landlord_fname = db.Column(db.String(100),nullable=False)
    landlord_lname = db.Column(db.String(100),nullable=False)
    landlord_email = db.Column(db.String(100),nullable=False,unique=True)
    landlord_phone = db.Column(db.String(100),nullable=True,unique=True)
    landlord_password = db.Column(db.String(200),nullable=False)
    address = db.Column(db.String(100),nullable=True)
    profile_pictures = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Enum("active", "inactive"), nullable=False, default="active")
    state_id = db.Column(db.ForeignKey("state_table.state_id"),nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    states = db.relationship("States", backref="state")

    def __str__(self):
        return f'{self.landlord_id}'

class States(db.Model):
    __tablename__= 'state_table'

    state_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(100), nullable=False, unique=True)

    def __str__(self):
        return f"{self.state_id}"


class Tenant(db.Model):
    __tablename__ = "tenant_details"

    tenant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_fname = db.Column(db.String(100), nullable=False)
    tenant_lname = db.Column(db.String(100), nullable=False)
    tenant_email = db.Column(db.String(100), nullable=False, unique=True)
    tenant_phone = db.Column(db.String(100), nullable=True, unique=True)
    tenant_password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Enum("active", "inactive"), nullable=False, default="active")
    profile_pictures = db.Column(db.String(200), nullable=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.tenant_id}"


class Vacant(db.Model):
    __tablename__ = "vacant_houses"

    house_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_price = db.Column(db.Numeric(10,2), nullable=False)
    landlord_id= db.Column(db.ForeignKey('landlord_details.landlord_id',ondelete="CASCADE"),nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    house_status = db.Column(db.Enum("active", "inactive"), nullable=False, default="active")
    house_type_id = db.Column(db.ForeignKey("house_type.house_id"), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    date_listed = db.Column(db.DateTime, default=datetime.utcnow)

    pictures = db.relationship("Pictures", backref=db.backref("property",cascade="all, delete"))
    landlord = db.relationship("Landlord", backref=db.backref("vacantdeets",cascade="all, delete"))

    def __str__(self):
        return f"{self.house_id}"


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("tenant_details.tenant_id",ondelete="CASCADE"))
    property_id = db.Column(db.Integer, db.ForeignKey("vacant_houses.house_id",ondelete="CASCADE"))

    user = db.relationship("Tenant", backref=db.backref("bookmarks",cascade="all, delete"))
    property = db.relationship("Vacant", backref=db.backref("bookmarked_by",cascade="all, delete"))

    def __str__(self):
        return f"{self.id}"
