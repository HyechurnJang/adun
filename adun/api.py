# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 2.
@author: HyechurnJang
'''

import json
import requests

class EngineAPI:
    
    def __init__(self, pipe='http://localhost:8080'):
        self.pipe = pipe
        self.headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}
        self.session = requests.Session()
    
    def close(self):
        self.session.close()
    
    def getEPG(self, id=None):
        url = self.pipe + '/epg'
        if id != None: url += '/%d' % id
        resp = self.session.get(url)
        if resp.status_code != 200:
            if id != None: return None
            else: return []
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getEPGHist(self):
        url = self.pipe + '/hist/epg'
        resp = self.session.get(url)
        if resp.status_code != 200: return []
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def setEPG(self, id, ac=None, qvlan=None):
        data = {}
        if ac != None: data['ac'] = ac
        if qvlan != None: data['qvlan'] = qvlan
        if not data: return False
        url = self.pipe + '/epg/%d' % id
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: return False
        if 'error' in resp.json(): return False
        return True
    
    def getEP(self, id=None):
        url = self.pipe + '/ep'
        if id != None: url += '/%d' % id
        resp = self.session.get(url)
        if resp.status_code != 200:
            if id != None: return None
            else: return []
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getEPHist(self):
        url = self.pipe + '/hist/ep'
        resp = self.session.get(url)
        if resp.status_code != 200: return []
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data

    def getMacIP(self, id=None):
        url = self.pipe + '/macip'
        if id != None: url += '/%d' % id
        resp = self.session.get(url)
        if resp.status_code != 200:
            if id != None: return None
            else: return []
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def setMacIPwithDN(self, tn, ap, epg, mac, ip, name=None):
        data = {'tn' : tn, 'ap' : ap, 'epg' : epg, 'mac' : mac, 'ip' : ip}
        if name != None: data['name'] = name
        url = self.pipe + '/macip'
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: return False
        if 'error' in resp.json(): return False
        return True
    
    def setMacIPwithID(self, id, mac, ip, name=None):
        data = {'mac' : mac, 'ip' : ip}
        if name != None: data['name'] = name
        url = self.pipe + '/macip/%d' % id
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: return False
        if 'error' in resp.json(): return False
        return True
    
    def delMacIP(self, id):
        url = self.pipe + '/macip/%d' % id
        resp = self.session.delete(url)
        if resp.status_code != 200: return False
        if 'error' in resp.json(): return False
        return True

engine = EngineAPI()