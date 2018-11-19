from flask import render_template
from apps import app
from apps.auth import login_required
from apps.models import User,Asset,Platforms

@app.route('/')
@login_required
def index():
    users_count = User.select().count()
    assets_count = Asset.select().count()
    platform_count = Platforms.select().count()
    return render_template('base/index.html',**locals())