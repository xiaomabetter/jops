from marshmallow import schema,fields,Schema
from app.models import Terminal,Session,Session_Terminal,Task,Task_Terminal,Command
import datetime

class TerminalSerializer(Schema):
    id = fields.Function(lambda obj: str(obj.id))
    name = fields.String(required=True)
    remote_addr = fields.String(required=True)
    command_storage = fields.String(default='default')
    replay_storage = fields.String(default='default')
    is_accepted = fields.Boolean()
    is_deleted  = fields.Boolean()
    date_created  = fields.DateTime()
    is_alive = fields.Method('get_is_alive')
    session_online = fields.Method("get_session_online")

    def get_is_alive(self,obj):
        return True

    def get_session_online(self,obj):
        query_set = Session.select().join(Session_Terminal).\
                        where(Session_Terminal.terminal_id == obj.id,
                              Session.is_finished==False
                              )
        return query_set.count()

class SessionSerializer(Schema):

    id = fields.Function(lambda obj: str(obj.id))
    user = fields.String()
    asset = fields.String()
    system_user = fields.String()
    login_from = fields.String()
    remote_addr = fields.String()
    is_finished = fields.Boolean()
    has_replay = fields.Boolean()
    has_command = fields.Boolean()
    command_amount = fields.Method("get_command_amount")
    terminal = fields.Method("get_terminal_id")
    protocol = fields.String()
    date_start= fields.DateTime()
    date_interval = fields.Method("get_date_interval")

    def get_date_interval(self,obj):
        date_start = datetime.datetime.strptime(str(obj.date_start), "%Y-%m-%d %H:%M:%S")
        if obj.date_end:
            date_end = datetime.datetime.strptime(str(obj.date_end), "%Y-%m-%d %H:%M:%S")
        else:
            date_end = datetime.datetime.now()
        return (date_end - date_start).seconds

    def get_terminal_id(self,obj):
        query = Session.select().join(Session_Terminal).where(Session_Terminal.session_id == obj.id)
        return query.id

    def get_command_amount(self,obj):
        query = Command.select().where(Command.session == obj.id)
        return query.count()

class CommandSerializer(Schema):
    id = fields.Function(lambda obj: str(obj.id))
    name = fields.String(required=True)
    args = fields.Function(lambda obj: str(obj.args))
    is_finished = fields.Boolean()
    date_created = fields.DateTime()
    date_finished = fields.DateTime()
    terminal = fields.Method("get_terminal_id")

    def get_terminal_id(self,obj):
        query_set = Task_Terminal.select().join(Task).where(Task.id == obj.id)
        return query_set.id


class TaskSerializer(Schema):
    id = fields.Function(lambda obj: str(obj.id))
    name = fields.String(required=True)
    args = fields.Function(lambda obj: str(obj.args))
    is_finished = fields.Boolean()
    date_created = fields.DateTime()
    date_finished = fields.DateTime()
    terminal = fields.Method("get_terminal_id")

    def get_terminal_id(self,obj):
        query_set = Task_Terminal.select().join(Task).where(Task.id == obj.id)
        return query_set.id
