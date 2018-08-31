from flask import Blueprint

asset = Blueprint('asset', __name__)

from . import api

from .view import *