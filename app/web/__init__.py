from flask import Blueprint, render_template

# 名字，所在的包或模块
web = Blueprint('web', __name__)

from . import book
from . import gift
from . import main
from . import wish
from . import drift
from . import auth

@web.app_errorhandler(404)
def not_found(e):
    return render_template('404.html')
