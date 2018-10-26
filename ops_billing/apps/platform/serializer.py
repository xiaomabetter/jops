from marshmallow import fields,Schema

class PlatformSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    proxyport = fields.String()
    class Meta:
        fields = ('id','description','location','proxyport','platform_url','catagory','date_created')
