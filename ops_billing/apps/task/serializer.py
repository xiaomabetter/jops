from marshmallow import schema,fields,Schema

class TasksSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    taskname = fields.String()
    comment = fields.String()