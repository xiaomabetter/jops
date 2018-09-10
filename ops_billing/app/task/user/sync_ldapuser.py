import ldap
from app.models import ldap_conn,User,Groups
from app.utils.encrypt import encryption_md5
from app import config

def sync_ldapusers():
    all_users = ldap_conn.search_s(config.get('LDAP','BASE_DN'),ldap.SCOPE_SUBTREE)
    for ldapuser in all_users:
        if 'uid'  in ldapuser[0]:
            info = ldapuser[0].split(',')
            groupname = info[1].split('=')[1]
            _user  = {
                'username':info[0].split('=')[1],
                'password':encryption_md5(ldapuser[1]['userPassword'][0].decode()),
                'phone':ldapuser[1]['telephoneNumber'][0].decode(),
                'email':ldapuser[1]['mail'][0].decode(),
                'is_ldap_user':True
            }
            user = User.select().where(User.username == _user['username']).first()
            group = Groups.select().where(Groups.value == groupname).first()
            ROOT = Groups.root()
            if not group :
                group = ROOT.create_child(value=groupname)
            if group.parent != ROOT:
                group.parent = ROOT
                group.save()
            if  user:
                User.update(**_user).where(User.id == user.id).execute()
            else:
                user = User.create(**_user)
            if user.group.select().where(Groups.value == groupname).count() == 0:
                user.group.add(group.id)