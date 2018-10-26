from apps.models import Asset,Node,OpsRedis


class NodeAmount(object):
    @classmethod
    def sync_root_assets(self,):
        try:
            asset_types = Asset.asset_type()
            for asset_type in asset_types:
                key = '{}_{}'.format(asset_type, 'ROOT')
                asset_amount = Node.root().get_all_assets(asset_type)\
                    .filter(Asset.Status != 'Destroy').count()
                print(asset_amount)
                OpsRedis.set(key, asset_amount)
        except Exception as e:
            print(str(e))

    @classmethod
    def sync_node_assets(self,nodeid):
        try:
            asset_types = Asset.asset_type()
            if nodeid:
                node = Node.select().where(Node.id == nodeid).get()
                for asset_type in asset_types:
                    key = '{}_{}'.format(asset_type, node.value)
                    asset_amount = node.get_all_assets(asset_type)\
                                .filter(Asset.Status != 'Destroy').count()
                    OpsRedis.set(key,asset_amount)
        except Exception as e:
            logger(str(e))

    @classmethod
    def sync_all_node_assets(self):
        for node in Node.select():
            try:
                asset_types = Asset.asset_type()
                for asset_type in asset_types:
                    key = '{}_{}'.format(asset_type, node.value)
                    asset_amount = node.get_all_assets(asset_type)\
                                .filter(Asset.Status != 'Destroy').count()
                    OpsRedis.set(key,asset_amount)
            except Exception as e:
                logger(str(e))