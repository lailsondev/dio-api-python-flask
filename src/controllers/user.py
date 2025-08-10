from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import inspect

from src.models import User, db
from src.utils import requires_role

app = Blueprint('user', __name__, url_prefix='/users')

def _create_user():
    data = request.json
    user = User(
        username=data['username'],
        password=data['password'],
        role_id=data['role_id']
    )
    db.session.add(user)
    db.session.commit()

def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    
    return [
        {
            'id': user.id,
            'username': user.username,
            "role": {
                'id': user.role.id,
                'name': user.role.name
            }
        }
        for user in users
    ]   

@app.route('/')
@jwt_required()
@requires_role("admin")
def list_user():
    user_id = get_jwt_identity()
    user = db.get_or_404(User, int(user_id))
    
    if user.role.name != 'admin':
        return {"message": "User doesn't have access"}, HTTPStatus.FORBIDDEN
    
    return {"users": _list_users()}

@app.route('/', methods=['POST'])
@jwt_required()
@requires_role("admin")
def create_user():
    user_id = get_jwt_identity()
    user = db.get_or_404(User, user_id)
    
    if user.role.name != 'admin':
        return {"message": "User doesn't have access"}, HTTPStatus.FORBIDDEN
    
    _create_user()
    return {'message': 'User created!'}, HTTPStatus.CREATED
    
    
    
@app.route('/<int:user_id>')
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    
    return {
            'id': user.id,
            'username': user.username,
        }
    
@app.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.json
        
    mapper = inspect(User)
    for column in mapper.attrs:
        if column.key in data:
            setattr(user, column.key, data[column.key])
    db.session.commit()
        
    # attrs = ['username']
    # for attr in attrs:
    #     setattr(user, attr, data[attr])
    # db.session.commit()
    
    return [
        {
            'id': user.id,
            'username': user.username
        }
    ]
    
@app.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return "", HTTPStatus.NO_CONTENT