"""
Millen's admin view instantiation
Modified from Paul Durivage's elemental project base
https://github.com/angstwad/elemental/blob/master/elemental/view/admin.py
and
Supplemented with flask-admin example
https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
"""
from flask_admin.contrib import sqla
from MESAeveryday import admin
from MESAeveryday.models import User, Role, session

class AdminView(sqla.ModelView):
    # Prevent normal users from accessing admin view
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('landpage'))

admin.add_view(AdminView(Role,session))
admin.add_view(AdminView(User,session))
