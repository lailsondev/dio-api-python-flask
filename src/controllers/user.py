from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from sqlalchemy import inspect
from sqlalchemy.orm import joinedload

from src.models import User, db
from src.views.user import UserSchema, CreateUserSchema
from src.utils import requires_role
from src.app import bcrypt

app = Blueprint('user', __name__, url_prefix='/users')

def _create_user():
    """
    Função auxiliar para criar um novo usuário.
    Valida os dados de entrada e salva no banco de dados.
    """
    user_schema = CreateUserSchema()
    
    try:
        data = user_schema.load(request.json)    
    except ValidationError as err:
        # Retorna o dicionário de erros e o código de status 422.
        return err.messages, HTTPStatus.UNPROCESSABLE_ENTITY
    
    user = User(
        username = data['username'],
        password = bcrypt.generate_password_hash(data['password']),
        role_id = data['role_id']
    )
    
    db.session.add(user)
    db.session.commit()        
    
    return {'message': 'User created!'}, HTTPStatus.CREATED

# @jwt_required()
# @requires_role('admin')
def _list_users():
    query = db.select(User).options(joinedload(User.role))
    users = db.session.execute(query).scalars()
    
    users_schema = UserSchema(many=True)
    return users_schema.dump(users)

@app.route('/', methods=['GET', 'POST'])
def list_or_create_user():
    """
    Endpoint principal para o recurso 'user'.
    Lida com requisições GET (listar) e POST (criar).
    """
    if request.method == 'GET':
        return {"users": _list_users()}
    else:
        return _create_user()
    
    
    
@app.route('/<int:user_id>')
def get_user(user_id):
    """User detail view.
    ---
    get:
      tags:
        - user
      parameters:
        - in: path
          name: user_id
          required: true
          schema: UserIdParameter
          description: O ID do usuário a ser buscado.
      responses:
        200:
          description: Successful operation
          content:
            application/json:
              schema: UserSchema
        404:
          description: User not found
    """
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
    """User delete view.
    ---
    delete:
      tags:
        - user
      summary: Deletes a user
      description: delete a user
      parameters:
        - in: path
          name: user_id
          required: true
          schema: UserIdParameter
          description: O ID do usuário a ser buscado.
      responses:
        204:
          description: Successful operation
        404:
          description: User not found
    """
    user = db.get_or_404(User, user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return "", HTTPStatus.NO_CONTENT