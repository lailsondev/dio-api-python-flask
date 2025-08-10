from src.app import ma
from src.views.role import RoleSchema
from marshmallow import fields
from src.models.user import User

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
    
    id = ma.auto_field()
    username = ma.auto_field()
    # id = fields.Int(dump_only=True)
    # username = fields.String(required=True)
    # role_id = fields.Int(load_only=True, required=True)
    role = ma.Nested(RoleSchema, dump_only=True)
    
class UserIdParameter(ma.Schema):
    user_id = fields.Int(required=True, strict=True)

class CreateUserSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    role_id = fields.Int(required=True, strict=True)