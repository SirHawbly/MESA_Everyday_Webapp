"""
Modified from flask-admin & flask-security tutorial
https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
"""
from flask import url_for, redirect
from flask_admin.contrib import sqla
from flask_security import current_user

# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # push back to landing page
                return redirect(url_for('landpage'))


