from ldap3 import Server, Connection, ALL,SUBTREE,ALL_ATTRIBUTES,MODIFY_REPLACE
import json
from app import config
from app import get_logger
logger = get_logger(__name__)

LDAP_SERVER = config.get('LDAP','LDAP_SERVER')
BASE_DN = config.get('LDAP','BASE_DN')
ROOT_DN = config.get('LDAP','ROOT_DN')
ROOT_DN_PASS = config.get('LDAP','ROOT_DN_PASS')

class LDAPTool(object):
    def __init__(self,ldap_uri=None,base_dn=None,manager_dn=None,password=None):
        self.manager_dn = manager_dn
        self.password = password
        self.base_dn = base_dn
        server =  Server(ldap_uri,get_info=ALL)
        try:
            self.conn = Connection(server,self.manager_dn,
                                        self.password,auto_bind=True,pool_keepalive=30,
                                        pool_size=10,pool_name='easemob',pool_lifetime=600)
        except Exception as e:
            self.conn.open();self.conn.bind()
            logger.error('ldap conn失败，原因为: %s' % str(e))

    def ldap_search_user(self, username=None):
        self.conn.open()
        if username:
            search_filter = f'(&(objectclass=inetOrgPerson)(uid={username}))'
        else:
            search_filter = f'(objectclass=inetOrgPerson)'
        result = self.conn.search(search_base=BASE_DN,search_filter=search_filter,
                                                    search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
        if not result:
            return result
        entry_list = []
        for entry in self.conn.entries:
            attributes = json.loads(entry.entry_to_json())['attributes']
            entry_list.append({
                'username':attributes['cn'][0],
                'chinese_name':attributes['sn'][0],
                'email':attributes['mail'][0] if attributes.get('mail') else None,
                'password':attributes['userPassword'][0] if attributes.get('userPassword') else None,
                'phone':attributes['telephoneNumber'][0] if attributes.get('telephoneNumber') else None,
                'department': entry.entry_dn.split(',')[1].split('=')[1],
                'is_ldap_user':True
            })
        return entry_list

    def ldap_add_user(self, ou,username, password,email=None,telephoneNumber=None):
        self.conn.open()
        attributes = {'objectClass': ['inetOrgPerson'],'cn':username,'sn':username}
        attributes['userPassword'] = password
        if email:
            attributes['mail'] = f'{email}'
        elif telephoneNumber:
            attributes['telephoneNumber'] = [f'{telephoneNumber}']
        result = self.conn.add(f'uid={username},ou={ou},{self.base_dn}',attributes=attributes)
        return result

    def ldap_update_user(self, username, ou,new_password='',mail='',telephoneNumber=''):
        self.conn.open()
        if not ou:
            userinfo = self.ldap_search_user(username=username)
            if userinfo:
                userinfo = userinfo[0]
            else:
                return False
            ou = userinfo.get('department')
        if new_password:
            result = self.conn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                 {'userPassword':[(MODIFY_REPLACE,f'{new_password}')]})
        elif mail:
            result = self.conn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                      {'mail':[(MODIFY_REPLACE,f'{mail}')]})
        elif telephoneNumber:
            result = self.conn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                      {'telephoneNumber':[(MODIFY_REPLACE,[f'{telephoneNumber}'])]})
        else:result = False
        return result

    def ldap_modify_user(self,username,newusername):
        self.conn.open()
        userinfo = self.ldap_search_user(username=username)
        if userinfo:
            userinfo = userinfo[0]
        else:return False
        ou = userinfo.get('department')
        result = self.conn.modify_dn(f'uid={username},ou={ou},{self.base_dn}',f'ou={newusername}')
        return result

    def ldap_move_user(self,username,newou):
        self.conn.open()
        userinfo = self.ldap_search_user(username=username)
        if userinfo:
            userinfo = userinfo[0]
        else:return False
        ou = userinfo.get('department')
        result = self.conn.modify_dn(f'uid={username},ou={ou},{self.base_dn}',f'uid={username}',
                                     new_superior=f'ou={newou},{self.base_dn}')
        return result

    def ldap_test_ou_exist(self,ou):
        self.conn.open()
        result = self.conn.search(f'{BASE_DN}', f'(&(objectclass=top)(ou={ou}))')
        return result

    def ldap_add_ou(self, ou):
        self.conn.open()
        result = self.conn.add(f'ou={ou},{self.base_dn}','organizationalUnit')
        return result

    def ldap_delete_ou(self, ou):
        self.conn.open()
        result = self.conn.delete(f'ou={ou},{self.base_dn}')
        return result

    def ldap_modify_ou(self,ou,newou):
        self.conn.open()
        result = self.conn.modify_dn(f'ou={ou},{self.base_dn}',f'ou={newou}')
        return result

    def ldap_delete_user(self, ou,username):
        self.conn.open()
        result = self.conn.delete(f'uid={username},ou={ou},{self.base_dn}')
        return result

    def gather_result(self):
        msg = ','.join([self.conn.result['description'],self.conn.result['message']])
        return msg

ldapconn = LDAPTool(LDAP_SERVER, BASE_DN, ROOT_DN, ROOT_DN_PASS)