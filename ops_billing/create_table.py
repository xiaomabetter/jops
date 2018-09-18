from app.models import *

def create_table():
    db.connect()
    create_tables = [
        Asset, Node, Bill, Asset_Node,Service,Asset_Service,Asset_Create_Record,Account,Asset_Account,
        SystemUser,Asset_Create_Template,
        AssetPermission,AssetPerm_Assets,AssetPerm_Nodes,AssetPerm_SystemUser,AssetPerm_Users,AssetPerm_Groups,
        Groups, User_Group,User,UserLoginLog,
        Sync_Bill_History,Tasks
    ]
    db.create_tables(create_tables)

create_table()
