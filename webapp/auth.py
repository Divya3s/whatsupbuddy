from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for


bp = Blueprint("auth", __name__, url_prefix="/auth")