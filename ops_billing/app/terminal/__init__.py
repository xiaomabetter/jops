from flask import Blueprint

terminal = Blueprint('terminal',__name__)

from .serializer import *

from .view import  *