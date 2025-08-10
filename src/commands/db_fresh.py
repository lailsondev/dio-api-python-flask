import click
from flask.cli import with_appcontext
from src.models.base import db

@click.group('db_fresh')
def db_fresh_group():
    """Drops all tables, recreates them, and runs seed data."""
    pass

@db_fresh_group.command('all')
@with_appcontext
def fresh_all_command():
    """Drops all tables and recreates them."""
    click.echo('Dropping all tables...')
    db.drop_all()
    click.echo('Creating all tables...')
    db.create_all()
    click.echo('Database fresh! ✨')