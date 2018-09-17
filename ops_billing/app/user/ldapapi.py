from ldap3 import Server, Connection, ALL,SUBTREE,ALL_ATTRIBUTES,MODIFY_REPLACE
from ldap3.abstract.entry import Entry
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
            self.ldapconn = Connection(server,self.manager_dn,self.password,auto_bind=True)
        except Exception as e:
            logger.error('ldap conn失败，原因为: %s' % str(e))

    def ldap_search_user(self, username=None):
        try:
            self.ldapconn.search(self.base_dn,f'(&(objectclass=inetOrgPerson)(uid={username}))',
                                                        search_scope=SUBTREE,attributes=ALL_ATTRIBUTES)
            entries = self.ldapconn.entries
            if len(entries) >=  1:
                if not isinstance(entries[0],Entry):
                    return None
                result = json.loads(entries[0].entry_to_json())['attributes']
                userinfo = {
                    'mail':result['mail'][0] if result.get('mail') else None,
                    'userPassword':result['userPassword'][0] if result.get('userPassword') else None,
                    'telephoneNumber':result['telephoneNumber'][0] if result.get('telephoneNumber') else None,
                    'groupname':entries[0].entry_dn.split(',')[1].split('=')[1]
                }
                return userinfo
            else:
                return None
        except Exception as e:
            logger.error('ldap search %s 失败，原因为: %s' % (username, str(e)))
            return None

    def ldap_add_user(self, ou,username, password,email=None,telephoneNumber=None):
        attributes = {'objectClass': ['inetOrgPerson'],'cn':username,'sn':username}
        attributes['userPassword'] = password
        if email:
            attributes['mail'] = f'{email}'
        elif telephoneNumber:
            attributes['telephoneNumber'] = [f'{telephoneNumber}']
        result = self.ldapconn.add(f'uid={username},ou={ou},{self.base_dn}',attributes=attributes)
        return result

    def ldap_add_ou(self, ou):
        result = self.ldapconn.add(f'ou={ou},{self.base_dn}')
        return result

    def ldap_delete_user(self, ou,username):
        try:
            result = self.ldapconn.delete(f'uid={username},ou={ou},{self.base_dn}')
            return result
        except Exception as e:
            return False

    def ldap_update_user(self, username, ou,new_password=None,mail=None,telephoneNumber=None):
        if not ou:
            userinfo = self.ldap_search_user(username=username)
            ou = userinfo.get('groupname')
        try:
            if new_password:
                self.ldapconn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                          {'userPassword':[(MODIFY_REPLACE,f'{new_password}')]})
            elif mail:
                self.ldapconn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                          {'mail':[(MODIFY_REPLACE,f'{mail}')]})
            elif telephoneNumber:
                self.ldapconn.modify(f'uid={username},ou={ou},{self.base_dn}',
                                          {'telephoneNumber':[(MODIFY_REPLACE,[f'{telephoneNumber}'])]})
            return True
        except Exception as e:
            logger.error("%s 更新失败，原因为: %s" % (username, str(e)))
            return False

ldapconn = LDAPTool(LDAP_SERVER, BASE_DN, ROOT_DN, ROOT_DN_PASS)

# for test
def main():
    ldap = LDAPTool('ldap://123.56.239.63:389','dc=easemob,dc=com','Manager','Easemob.')
    print(ldap.ldap_search_user('mazhenjie1'))
    print(ldap.ldap_update_user('mazhenjie1', 'PAAS',mail='test@easemob.com',new_password='123456'))
    print(ldap.ldap_search_user('mazhenjie1'))
    print(ldap.ldap_add_user(ou='PAAS',username='mmmm',password='mmmmm'))
    print(ldap.ldap_search_user(username='mmmm'))
if __name__ == '__main__':
    main()