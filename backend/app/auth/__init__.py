#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Blueprint
"""

from flask import Blueprint
from flask_login import LoginManager

auth_bp = Blueprint('auth', __name__, template_folder='templates')
login_manager = LoginManager()

from . import routes
