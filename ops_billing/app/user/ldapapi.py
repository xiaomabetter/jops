#!/usr/bin/env python
# -*- coding:utf-8 -*-

import ldap
import ldap3
import ldap.modlist as modlist
import sys
import logging
logger = logging.getLogger()
from SSOadmin import settings
# 登陆 地址
LDAP_URI = settings.AUTH_LDAP_SERVER_URI
# 登陆 账户
LDAP_USER = settings.AUTH_LDAP_BIND_DN
# 登陆 密码
LDAP_PASS = settings.AUTH_LDAP_BIND_PASSWORD
# 默认 区域
BASE_DN = settings.base_dn


class LDAPTool(object):
    def __init__(self,ldap_uri=None,base_dn=None,user=None,password=None):
        if not ldap_uri:
            ldap_uri = LDAP_URI
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            self.admin_user = LDAP_USER
        if not password:
            self.admin_password = LDAP_PASS
        try:
            self.ldapconn = ldap.initialize(ldap_uri)  # 老版本使用open方法
            self.ldapconn.simple_bind(self.admin_user, self.admin_password)  # 绑定用户名、密码
        except ldap.LDAPError as e:
            logger.error('ldap conn失败，原因为: %s' % str(e))

    def ldap_search_dn(self, value=None, value_type='uid'):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        if value_type == 'cn':
            searchFilter = "cn=" + value
        else:
            searchFilter = "uid=" + value
        try:
            ldap_result_id = obj.search(
                base=self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data
            else:
                return None
        except ldap.LDAPError as e:
            logger.error('ldap search %s 失败，原因为: %s' % (value, str(e)))

    def ldap_get_user(self, uid=None):
        result = None
        try:
            search = self.ldap_search_dn(value=uid, value_type=uid)
            if search is None:
                raise ldap.LDAPError('未查询到相应 id')
            for user in search:
                if user[1]['uid'][0] == uid:
                    result = {
                        'uid': uid,
                        'mail': user[1]['mail'][0],
                        'cn': user[1]['cn'][0],
                    }
        except Exception as e:
            logger.error('获取用户%s 失败，原因为: %s' % (uid, str(e)))
        return result

    def __ldap_getgid(self, cn="员工"):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "cn=" + cn
        try:
            ldap_result_id = obj.search(
                base="ou=Group,%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data[0][1].get('gidNumber')[0]
            else:
                return None
        except ldap.LDAPError as e:
            logger.error('获取gid失败，原因为: %s' % str(e))

    def __get_max_uidNumber(self):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ['uidNumber']
        searchFilter = "uid=*"

        try:
            ldap_result = obj.search(
                base="ou=People,%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_set = []
            while True:
                result_type, result_data = obj.result(ldap_result, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(int(result_data[0][1].get('uidNumber')[0]))
            return max(result_set) + 1
        except ldap.LDAPError as e:
            logger.error('获取最大uid失败，原因为: %s' % str(e))

    def ldap_add_user(self, cn, mail, username, password):
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3

            addDN = "uid=%s,ou=People,%s" % (username, BASE_DN)
            attrs = {}
            attrs['objectclass'] = ['top', 'person', 'inetOrgPerson', 'posixAccount', 'organizationalPerson']
            attrs['cn'] = str(cn)
            attrs['homeDirectory'] = str('/home/%s' % username)
            attrs['loginShell'] = '/bin/bash'
            attrs['mail'] = str(mail)
            attrs['sn'] = str(username)
            attrs['uid'] = str(username)
            attrs['userPassword'] = str(password)
            attrs['uidNumber'] = str(self.__get_max_uidNumber())
            attrs['gidNumber'] = self.__ldap_getgid(cn='员工')
            ldif = ldap.modlist.addModlist(attrs)
            obj.add_s(addDN, ldif)
            obj.unbind_s()
            result = True
        except ldap.LDAPError as e:
            logger.error("生成用户%s 失败，原因为: %s" % (username, str(e)))
        return result

    def check_user_belong_to_group(self, uid, group_cn='员工'):
        result = None
        try:
            search = self.ldap_search_dn(value=group_cn, value_type='cn')
            if search is None:
                raise ldap.LDAPError('未查询到相应 id')

            member_list = search[0][1].get('memberUid', [])
            if uid in member_list:
                result = True
        except ldap.LDAPError as e:
            logger.error('获取用户%s与组%s关系失败，原因为: %s' % (uid, group_cn, str(e)))
        return result

    def check_user_status(self, uid):
        result = 404
        try:
            target_cn = self.ldap_get_user(uid=uid)
            if target_cn is None:  # 如未查到用户，记录日志，但不算错误，后边有很多地方会验证用户是否存在
                result = 404
                logger.debug("%s uid未查询到" % uid)
            else:
                if self.check_user_belong_to_group(uid=uid, group_cn='黑名单'):
                    result = 403
                else:
                    result = 200
        except ldap.LDAPError as e:
            logger.error("%s 检查用户状态失败，原因为: %s" % (uid, str(e)))
        return result

    def ldap_update_password(self, uid, new_password):
        """
        更新密码
        :param uid: 用户uid，新password
        :return: True|None
        """
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3
            modifyDN = "uid=%s,ou=People,%s" % (uid, BASE_DN)
            # 因为是更新密码，如用passwd_s方法需要oldpassword，如果用下边方法，是增加一个新密码，而不是替换，而我们的需求是重置密码
            # old_password = {'userPassword': ''}
            # new_password = {'userPassword': new_password}
            # ldif = modlist.modifyModlist(old_password, new_password)
            # obj = modlist.modifyModlist(modifyDN, ldif)
            # 以下方法实现密码替换的效果，第二个参数就是要替换的属性名,可以变更其他属性
            obj.modify_s(modifyDN, [(ldap.MOD_REPLACE, 'userPassword', [str(new_password)])])
            obj.unbind_s()
            result = True
        except ldap.LDAPError as e:
            logger.error("%s 密码更新失败，原因为: %s" % (uid, str(e)))
        return result

# for test
def main():
    # print type(LDAPTool().get_max_uidNumber())
    # print(LDAPTool().ldap_search_dn(value='qudong'))
    # print(LDAPTool().check_user_belong_to_group('qudong', '黑名单'))
    # print LDAPTool().ldap_get_user(uid='qudong')
    # print(LDAPTool().check_user_and_email(uid='qudong', email='qudong@ssotest.com'))
    # s=LDAPTool()
    # print s.ldap_add_user('哈喽2','test222@ssotest.com','test222','test222')
    # print(s._LDAPTool__ldap_getgid('黑名单'))
    # print(LDAPTool().ldap_update_password('qudong','111111'))
    pass

if __name__ == '__main__':
    main()