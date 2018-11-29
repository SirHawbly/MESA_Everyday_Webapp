"""
Modified from flask-admin & flask-security tutorial
https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
"""
from flask import Flask, url_for
import flask_admin
from flask_admin import helpers as admin_helpers
from flaskblog import MyModelView
from flask_security import Security, login_required, current_user
from flask_security.utils import encrypt_password

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create admin
admin = flask_admin.Admin(
    app,
    'Example: Auth',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Add model views
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(User, db.session))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

with app.app_context():
        super_user_role = Role(name='superuser')
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )
