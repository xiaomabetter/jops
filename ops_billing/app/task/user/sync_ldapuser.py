from app.models import User,Groups
from app.utils.encrypt import encryption_md5
from app.user.ldapapi import ldapconn

def sync_ldapusers():
    ldap_users = ldapconn.ldap_search_user()
    ROOT = Groups.root()
    for user in ldap_users:
        user['password'] = encryption_md5(user['password']) if user.get('password') else ''
        localuser = User.select().where(User.username == user.get('username')).first()
        department_name = user.get('department');user.pop('department')
        if department_name:
            department = Groups.select().where(Groups.value == department_name).first()
        else:department = None
        if localuser:
            User.update(**user).where(User.username == user.get('username')).execute()
            if not department:
                department = ROOT.create_child(value=department_name)
            if department.parent != ROOT:
                department.parent = ROOT
                department.save()
            if not department.is_ldap_group :
                department.is_ldap_group = True
                department.save()
            localuser.group.clear()
            localuser.group.add(department.id)
        else:
            newuser = User.create(**user)
            newuser.group.add(department.id)




'''
import ldap
from app.models.base import db
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
                'password':encryption_md5(ldapuser[1]['userPassword'][0].decode())
                                                if ldapuser[1].get('userPassword') else '',
                'phone':ldapuser[1]['telephoneNumber'][0].decode()
                                                if ldapuser[1].get('telephoneNumber') else '',
                'email':ldapuser[1]['mail'][0].decode()
                                                if ldapuser[1].get('mail') else '',
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
'''