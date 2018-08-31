from app import get_logger
from app.models import Asset,Node,OpsRedis

logger = get_logger(__name__)

class NodeAmount(object):
    @classmethod
    def sync_root_assets(self,):
        try:
            asset_types = Asset.asset_type()
            for asset_type in asset_types:
                key = '{}_{}'.format(asset_type, 'ROOT')
                asset_amount = Node.root().get_all_assets(asset_type).count()
                OpsRedis.set(key, asset_amount)
        except Exception as e:
            logger(str(e))

    @classmethod
    def sync_node_assets(self,nodeid):
        try:
            asset_types = Asset.asset_type()
            if nodeid:
                node = Node.select().where(Node.id == nodeid).get()
                for asset_type in asset_types:
                    key = '{}_{}'.format(asset_type, node.value)
                    asset_amount = node.get_all_assets(asset_type).count()
                    OpsRedis.set(key,asset_amount)
        except Exception as e:
            logger(str(e))