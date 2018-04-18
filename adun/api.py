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
    
    def getEPG(self, id=None, epg_wn=None):
        url = self.pipe + '/epg'
        if id != None: url += '?id=%d' % id
        elif epg_wn != None: url += '?epg_wn="%s"' % epg_wn
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def setEPG(self, id, ac=None, qvlan=None):
        data = {}
        if ac != None: data['ac'] = ac
        if qvlan != None: data['qvlan'] = qvlan
        if not data: return False
        url = self.pipe + '/epg?id=%d' % id
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: resp.raise_for_status()
        if 'error' in resp.json(): return False
        return True
    
    def getEP(self, id=None, epg_wn=None):
        url = self.pipe + '/ep'
        if id != None: url += '?id=%d' % id
        elif epg_wn != None: url += '?epg_wn="%s"' % epg_wn
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getMacIP(self, id=None, epg_wn=None):
        url = self.pipe + '/macip'
        if id != None: url += '?id=%d' % id
        elif epg_wn != None: url += '?epg_wn="%s"' % epg_wn
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def setMacIPwithID(self, id, mac, ip, name=None):
        data = {'mac' : mac, 'ip' : ip}
        if name != None: data['name'] = name
        url = self.pipe + '/macip?id=%d' % id
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: resp.raise_for_status()
        if 'error' in resp.json(): return False
        return True
    
    def setMacIPwithWN(self, epg_wn, mac, ip, name=None):
        data = {'mac' : mac, 'ip' : ip}
        if name != None: data['name'] = name
        url = self.pipe + '/macip?epg_wn="%s"' % epg_wn
        resp = self.session.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code != 200: resp.raise_for_status()
        if 'error' in resp.json(): return False
        return True
    
    def delMacIP(self, id):
        url = self.pipe + '/macip?id=%d' % id
        resp = self.session.delete(url)
        if resp.status_code != 200: resp.raise_for_status()
        if 'error' in resp.json(): return False
        return True
    
    def getEPGHist(self):
        url = self.pipe + '/hist/epg'
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getEPHist(self):
        url = self.pipe + '/hist/ep'
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getEPGTopo(self):
        url = self.pipe + '/topo/epg'
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data
    
    def getEPTopo(self, epg_wn):
        url = self.pipe + '/topo/ep?epg_wn="%s"' % epg_wn
        resp = self.session.get(url)
        if resp.status_code != 200: resp.raise_for_status()
        data = resp.json()
        if 'error' in data: raise Exception(data['error'])
        return data

engine = EngineAPI()