from src.app import ma
from marshmallow import fields

class RoleSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()