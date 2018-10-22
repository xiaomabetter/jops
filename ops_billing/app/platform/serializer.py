from marshmallow import fields,Schema

class PlatformSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)

    class Meta:
        fields = ('id','description','location','platform_url','catagory','date_created')
