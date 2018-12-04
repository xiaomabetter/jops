from marshmallow import fields,Schema,validates,ValidationError

class PlatformSerializer(Schema):
    id = fields.Function(lambda obj: obj.id.hex)
    proxyport = fields.String()
    platform_url  = fields.String()

    @validates('platform_url')
    def url_validate(self):
        pass

    class Meta:
        fields = ('id','description','location','proxyport','isproxy',
                    'platform_url','catagory','date_created')
