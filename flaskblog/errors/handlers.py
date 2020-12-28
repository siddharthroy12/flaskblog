from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(401)
def error_401(error):
    return render_template('errors/401.html'), 401

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500