from flask import Blueprint, request
from http import HTTPStatus
from sqlalchemy import inspect
from src.app import Role, db

app = Blueprint('role', __name__, url_prefix='/roles')

def _create_user():
    data = request.json
    user = Role(
        username=data['username'],
        password=data['password'],
        role_id=data['role_id']
    )
    db.session.add(user)
    db.session.commit()
    
@app.route('/', methods=['POST'])
def create_role():
    data = request.json
    role = Role(name=data['name'])
    db.session.add(role)
    db.session.commit()
    
    return {'message': 'Role created!'}, HTTPStatus.CREATED