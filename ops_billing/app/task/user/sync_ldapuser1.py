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