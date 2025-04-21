from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail

mail = Mail()


csrf=CSRFProtect()
def create_app():
    from pkg.models import db
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile("config.py")
    

    csrf.init_app(app)
    db.init_app(app)
    migrate = Migrate(app,db)
    mail.init_app(app)

    return app

app = create_app()

from pkg import user_route,admin_routes
