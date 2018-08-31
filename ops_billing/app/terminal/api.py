from app import get_logger, get_config
from flask import request,jsonify,make_response
from flask_restful import Api,Resource,reqparse
from app.auth import login_required,terminal_auth_token,Auth
from app.utils import trueReturn,falseReturn
from app.models import Terminal,Session,Session_Terminal,Task,Task_Terminal,Command
from .serializer import TerminalSerializer,TaskSerializer
import time,datetime,json

logger = get_logger(__name__)
cfg = get_config()

def get_terminal_id():
    token = request.headers.get('Authorization')
    payload = Auth.decode_auth_token(token, expire=False)
    tid = payload.get('data')['id']
    return tid

class TerminalListApi(Resource):
    @login_required
    def get(self):
        serializer = TerminalSerializer()
        query_set = Terminal.select().order_by(Terminal.name)
        result = serializer.dump(query_set,many=True)
        return jsonify({'results':result.data})

    @login_required
    def delete(self):
        args = reqparse.RequestParser().add_argument('id', type=str, location='json').parse_args()
        tid = args.get('id')
        Session_Terminal.delete().where(Session_Terminal.terminal_id == tid).execute()
        Task_Terminal.delete().where(Task_Terminal.terminal_id == tid).execute()
        Terminal.delete().where(Terminal.id == tid).execute()
        return jsonify({})

class TerminalDetailApi(Resource):
    @login_required
    def get(self,tid):
        query_set = Terminal.select().where(Terminal.id==tid)
        serializer = TerminalSerializer(many=True)
        data = serializer.dump(query_set).data[0]
        return jsonify(data)

class TerminalRegisterApi(Resource):
    def post(self):
        args = reqparse.RequestParser().add_argument('name', type=str, location='json').parse_args()
        name = args.get('name')
        remote_addr = request.remote_addr
        terminal = Terminal.filter(Terminal.name == name)
        if terminal:
            msg = 'Terminal name %s already used' % name
            data = {'msg':msg}
            return make_response(jsonify(data),409)

        terminal = Terminal.create(name=name,remote_addr=remote_addr)
        data = {"id": str(terminal.id), "msg": "Need accept"}
        return make_response(jsonify(data),201)

class TerminalTokenApi(Resource):
    def post(self):
        args = reqparse.RequestParser().add_argument('id', type=str, location='json').parse_args()
        tid = args.get('id')
        try:
            terminal = Terminal.select().where(Terminal.id == tid).first()
        except Terminal.DoesNotExist:
            terminal = None
        if terminal is None:
            return make_response('May be reject by administrator',401)
        if not terminal.is_accepted:
            return make_response("Terminal was not accepted yet",400)
        access_key = Auth.encode_auth_token(tid,int(time.time()))
        terminal.access_key = access_key
        terminal.save()
        data = {'id': tid, 'secret': access_key,"msg": "Need accept"}
        return make_response(jsonify(data), 200)

class TerminalStatusApi(Resource):
    @terminal_auth_token
    def post(self):
        args = reqparse.RequestParser().add_argument('session_online', type=str, location='json') \
                    .add_argument('sessions',type=dict,action='append',location='json').parse_args()
        print(request.data)
        tid = get_terminal_id()
        sessions_active = []
        if args.get('sessions') :
            for session_data in args.get('sessions'):
                session_in_db_ids = [str(sess.id) for sess in Session.select()]
                if session_data['id'] in session_in_db_ids:
                    Session.update(**session_data).where(Session.id == session_data['id'])
                else:
                    r = Session.create(**session_data)
                    r.terminal.add(tid)
                if not session_data["is_finished"]:
                    sessions_active.append(session_data["id"])

        sessions_in_db_active = Session.select().join(Session_Terminal).\
                                where(Session.is_finished==False,Session_Terminal.terminal_id==tid)
        for session in sessions_in_db_active:
            if str(session.id) not in sessions_active:
                session.is_finished = True
                session.date_end = datetime.datetime.now()
                session.save()

        serializer = TaskSerializer(many=True)
        task_query_set = Task.select().join(Task_Terminal).\
                                    where(Task_Terminal.terminal_id==tid and Task.is_finished==False)
        data = serializer.dump(task_query_set).data
        return make_response(jsonify(data),201)

class SessionListApi(Resource):
    @terminal_auth_token
    def post(self):
        tid = get_terminal_id()
        session = json.loads(request.data)
        instance = Session.create(**session)
        instance.terminal.add(tid)
        return make_response(jsonify({}), 201)

    @login_required
    def put(self):
        validated_session = []
        for session_id in json.loads(request.data):
            session = Session.select().where(Session.id==session_id).get()
            terminal = Session_Terminal.select().where(Session_Terminal.session_id==session_id).get()
            terminal_id = terminal.terminal_id.hex
            if session and not session.is_finished:
                validated_session.append(session_id)
                instance = Task.create(name="kill_session", args=session_id)
                instance.terminal.add(terminal_id)
        return jsonify(trueReturn(msg='Terminate task send, waiting ...'))

class SessionReplayApi(Resource):
    def post(self,sid):
        pass

class SessionCommandApi(Resource):
    @terminal_auth_token
    def post(self):
        command_list = json.loads(request.data)
        Command.insert_many(command_list).execute()
        return make_response(jsonify({}), 201)

class TaskReplayApi(Resource):
    @terminal_auth_token
    def patch(self,task_id):
        replay_data = json.loads(request.data)
        if replay_data['is_finished'] :
            r = Task.update(is_finished=True).where(Task.id == task_id).execute()
            if r :
                return jsonify(trueReturn(msg='ok'))
