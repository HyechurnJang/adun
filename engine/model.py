# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import re
from sql import *

db = Sql(File())

@model(db)
class EPG(Model):
    
    dn = String(256)
    ac = Boolean()
    useg = Boolean()
    qvlan = Integer()
    status = String(16)
    tstamp = String(64)
    deleted = Boolean()
    
    def __init__(self, dn, qvlan, status, tstamp, ac=False, useg=False, deleted=False):
        self.dn = dn
        self.ac = ac
        self.useg = useg
        self.qvlan = qvlan
        self.status = status
        self.tstamp = tstamp
        self.deleted = deleted
    
    def __repr__(self):
        return 'EPG(%s, %s)' % (self.dn, str(self.ac))
    
    def toDict(self):
        return {
            'id' : self.id,
            'dn' : self.dn,
            'ac' : self.ac,
            'useg' : self.useg,
            'qvlan' : self.qvlan,
            'status' : self.status,
            'tstamp' : self.tstamp,
            'deleted' : self.deleted
        }

@model(db)
class EP(Model):
    
    dn = String(256)
    epg_dn = String(256)
    path_dn = String(256)
    mac = String(24)
    ip = String(16)
    status = String(16)
    tstamp = String(64)
    deleted = Boolean()
    blocked = Boolean()
    
    def __init__(self, dn, path_dn, mac, ip, status, tstamp, deleted=False, blocked=False):
        self.dn = dn
        self.epg_dn = self.dn.split('/cep-')[0]
        self.path_dn = path_dn
        self.mac = mac
        self.ip = ip
        self.status = status
        self.tstamp = tstamp
        self.deleted = deleted
        self.blocked = blocked
    
    def __repr__(self):
        return 'EP(%s, %s, %s)' % (self.dn, self.ip, str(self.blocked))
    
    def toDict(self):
        return {
            'id' : self.id,
            'dn' : self.dn,
            'epg_dn' : self.epg_dn,
            'path_dn' : self.path_dn,
            'mac' : self.mac,
            'ip' : self.ip,
            'status' : self.status,
            'tstamp' : self.tstamp,
            'deleted' : self.deleted,
            'blocked' : self.blocked
        }

@model(db)
class MacIP(Model):
    
    epg_dn = String(256)
    mac = String(24)
    ip = String(16)
    name = String(128)
    
    def __init__(self, epg_dn, mac, ip, name=None):
        self.epg_dn = epg_dn
        self.mac = mac
        self.ip = ip
        if name != None: self.name = name
        else: self.name = '-'
    
    def __repr__(self):
        return 'MacIP(%s, %s, %s, %s)' % (self.name, self.mac, self.ip, self.epg_dn)
    
    def toDict(self):
        return {
            'id' : self.id,
            'epg_dn' : self.epg_dn,
            'mac' : self.mac,
            'ip' : self.ip,
            'name' : self.name
        }