from flask import Blueprint

platform = Blueprint('platform', __name__)

from .view import *