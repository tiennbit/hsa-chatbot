#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Blueprint
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from . import routes

