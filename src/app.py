import os

from flask import Flask, current_app
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.models.base import db
from flask_bcrypt import Bcrypt
from src.commands.db_fresh import db_fresh_group
from flask_marshmallow import Marshmallow

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin


migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
ma = Marshmallow()
spec = APISpec(
    title="Api Flask",
    version="1.0.0",
    openapi_version="3.0.3",
    info=dict(description="API Construída no aprendizado do Framework"),
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)

def create_app(environment=os.getenv('ENVIROMENT', 'development')):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(f"src.config.{environment.title()}Config")
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    from src.controllers import auth, role, user
    
    app.register_blueprint(user.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)
    
    @app.route('/docs')
    def docs():
        return spec.path(view=user.get_user).path(view=user.delete_user).to_dict()
    
    from flask import json
    from werkzeug.exceptions import HTTPException
    
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description
        })
        response.content_type = "application/json"
        return response
    
    app.cli.add_command(db_fresh_group)
    
    return app