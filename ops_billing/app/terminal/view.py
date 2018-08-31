from flask import render_template,request,flash,jsonify
from app.utils import generate_rsa_keys,model_to_form
from app.auth import login_required
from app.models import Terminal,Status,Session
from . import terminal
from .form import Terminal_Form
from datetime import datetime,timedelta
from .serializer import SessionSerializer

@terminal.route('/terminal/terminal/list',methods=['GET','POST'])
@login_required
def terminal_list():
    form = Terminal_Form()
    return render_template('terminal/terminal_list.html',form=form)

@terminal.route('/terminal/<type>/session/list',methods=['GET','POST'])
@login_required
def session_list(type):
    date_from = request.args.get('date_from','')
    date_to = request.args.get('date_to', '')
    if not date_from or not date_to:
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    serializer = SessionSerializer()
    if type == 'history':
        query_set = Session.select().order_by(Session.date_start.desc())
    elif type == 'online' :
        query_set = Session.select().where(Session.is_finished==False).order_by(Session.date_start.desc())
    session_list = serializer.dump(query_set, many=True).data
    user_list = list(set([session['user'] for session in session_list]))
    asset_list  = list(set([session['asset'] for session in session_list]))
    system_user_list  = list(set([session['system_user'] for session in session_list]))
    return render_template('terminal/session_list.html',**locals())

@terminal.route('/terminal/<tid>/update',methods=['GET','POST'])
@login_required
def terminal_update(tid):
    form = Terminal_Form()
    if request.method == 'POST' and form.validate():
        row = request.form.to_dict()
        row['is_accepted'] = True
        row.pop('csrf_token')
        try:
            r = Terminal.update(**row).where(Terminal.id == tid).execute()
            return jsonify({'success': True})
        except Exception as e :
            return jsonify({'success': False,'msg':e})
    return render_template('terminal/terminal_list.html',form=form)