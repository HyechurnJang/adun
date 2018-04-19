# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import json
import datetime
from json import JSONEncoder
from pygics import Lock
from acidipy import Controller, Event 
from model import EPG, EP, MacIP

class Tracker:
    
    class TrackerEncoder(JSONEncoder):
        def default(self, obj): return obj.toDict()
    
    class EPGEvent(Event):
        
        def __init__(self, tracker):
            self.tracker = tracker
        
        def handle(self, status, obj):
            try: self.__epg_event_handle__(status, obj)
            except Exception as e: print 'Except EPG Event >> %s' % str(e)
        
        def __epg_event_handle__(self, status, obj):
            if status == 'created':
                epg = EPG(obj['dn'], self.tracker.qvlan, status, obj['modTs']).create()
                self.tracker.lock.on()
                try:
                    self.tracker.epgs[epg.dn] = epg
                    self.tracker.eps[epg.dn] = {}
                except Exception as e:
                    self.tracker.lock.off()
                    raise Exception('Create EPG >> %s' % str(e))
                self.tracker.lock.off()
                print 'CREATE %s' % str(epg)
            elif status == 'deleted':
                dn = obj['dn']
                self.tracker.lock.on()
                try:
                    self.tracker.eps.pop(dn)
                    epg = self.tracker.epgs.pop(dn)
                except Exception as e:
                    self.tracker.lock.off()
                    raise Exception('Delete EPG >> %s' % str(e))
                self.tracker.lock.off()
                epg.deleted = True
                epg.update()
                epg = EPG(dn, epg.qvlan, status, obj['modTs'], deleted=True).create()
                print 'DELETE %s' % str(epg)
    
    class EPEvent(Event):
        
        def __init__(self, tracker):
            self.tracker = tracker
        
        def handle(self, status, obj):
            try: self.__ep_event_handle__(status, obj)
            except Exception as e: print 'Except EP Event >> %s' % str(e)
        
        def __ep_event_handle__(self, status, obj):
            if status == 'created':
                try: path_dn = obj.Class('fvRsCEpToPathEp').list(detail=True)[0]['tDn']
                except: path_dn = ''
                ep = EP(obj['dn'], path_dn, obj['mac'], obj['ip'], status, obj['modTs']).create()
                self.tracker.lock.on()
                try:
                    self.tracker.eps[ep.epg_dn][ep.dn] = ep
                except Exception as e:
                    self.tracker.lock.off()
                    raise Exception('Create EP >> %s' % str(e))
                self.tracker.lock.off()
                print 'CREATE %s' % str(ep)
            elif status == 'modified':
                epg_dn = obj['dn'].split('/cep-')[0]
                if 'ip' not in obj: return
                ip = obj['ip']
                ip_mod = False
                self.tracker.lock.on()
                try:
                    ep = self.tracker.eps[epg_dn][obj['dn']]
                    if ip != '0.0.0.0' and ip != ep.ip:
                        ep.deleted = True
                        ep.update()
                        ep = EP(ep.dn, ep.path_dn, ep.mac, ip, status, obj['modTs']).create()
                        self.tracker.eps[epg_dn][ep.dn] = ep
                        ip_mod = True
                        print 'UPDATE %s' % str(ep)
                except Exception as e:
                    self.tracker.lock.off()
                    raise Exception('Update EP >> %s' % str(e))
                self.tracker.lock.off()
                if not ip_mod: return
            elif status == 'deleted':
                ep_dn = obj['dn']
                epg_dn = ep_dn.split('/cep-')[0]
                self.tracker.lock.on()
                try:
                    ep = self.tracker.eps[epg_dn].pop(ep_dn)
                except Exception as e:
                    self.tracker.lock.off()
                    raise Exception('Delete EP >> %s' % str(e))
                self.tracker.lock.off()
                ep.deleted = True
                ep.update()
                ep = EP(ep.dn, ep.path_dn, ep.mac, ep.ip, status, obj['modTs'], deleted=True).create()
                print 'DELETE %s' % str(ep)
            else: return
            self.tracker.lock.on()
            epg = self.tracker.epgs[ep.epg_dn]
            self.tracker.inspect(epg, ep)
            self.tracker.lock.off()
    
    def __init__(self, apic_ip, username, password, qvlan=0, debug=False):
        
        print '''
ADUN Engine Variables
  - APIC CONN IP  : %s
  - APIC USERNAME : %s
  - APIC PASSWORD : %s
  - APIC DEBUG : %s
  - DEFAULT QVLAN : %d
''' % (apic_ip, username, password, str(debug), qvlan)
        
        self.epgs = {}
        self.eps = {}
        self.macips = {}
        self.lock = Lock()
        self.qvlan = qvlan
        self.ctrl = Controller(apic_ip, username, password, debug=debug)
        self.__init_data__()
        
    def __init_data__(self):
        #=======================================================================
        # Make Current
        #=======================================================================
        for macip in MacIP.list():
            if macip.epg_dn not in self.macips: self.macips[macip.epg_dn] = {}
            self.macips[macip.epg_dn][macip.mac] = macip
            
        for epg_obj in self.ctrl.EPG.list(detail=True):
            epgs = [epg for epg in EPG.list(EPG.dn==epg_obj['dn'])]
            useg = True if epg_obj['isAttrBasedEPg'] == 'yes' else False
            if not epgs: epg = EPG(epg_obj['dn'], self.qvlan, 'inherited', epg_obj['modTs'], useg=useg).create()
            else:
                epg = max(epgs, key=lambda e: e.id)
                if epg.deleted == True:
                    epg = EPG(epg_obj['dn'], self.qvlan, 'inherited', epg_obj['modTs'], ac=epg.ac, useg=useg).create()
            self.epgs[epg.dn] = epg
            self.eps[epg.dn] = {}
        
        for ep_obj in self.ctrl.Endpoint.list(detail=True):
            try: path_dn = ep_obj.Class('fvRsCEpToPathEp').list(detail=True)[0]['tDn']
            except: path_dn = ''
            eps = [ep for ep in EP.list(EP.dn==ep_obj['dn'])]
            if not eps: ep = EP(ep_obj['dn'], path_dn, ep_obj['mac'], ep_obj['ip'], 'inherited', ep_obj['modTs']).create()
            else:
                ep = max(eps, key=lambda e: e.id)
                if ep.deleted == True:
                    ep = EP(ep_obj['dn'], path_dn, ep_obj['mac'], ep_obj['ip'], 'inherited', ep_obj['modTs']).create()
            self.eps[ep.epg_dn][ep.dn] = ep
        
        #=======================================================================
        # Make Unknown to Deleted
        #=======================================================================
        now = datetime.datetime.now().strftime('%Y-%m-%dT%X.%f')[:-3]
        
        epgs = EPG.list()
        for epg in epgs:
            if epg.deleted == False and epg.dn not in self.epgs:
                epg.deleted = True
                epg.update()
                EPG(epg.dn, epg.qvlan, 'deleted', now, ac=epg.ac, useg=epg.useg, deleted=True).create()
        
        eps = EP.list()
        for ep in eps:
            if ep.deleted == False and ep.dn not in self.eps[ep.epg_dn]:
                ep.deleted = True
                ep.update()
                EP(ep.dn, ep.path_dn, ep.mac, ep.ip, 'deleted', now, deleted=True).create()
        
        self.ctrl.EPG.event(Tracker.EPGEvent(self))
        self.ctrl.Endpoint.event(Tracker.EPEvent(self))
        
    def setEPGAC(self, epg_dn, ac=None, qvlan=None):
        if epg_dn not in self.epgs: return None
        epg = self.epgs[epg_dn]
        mod = False
        if ac != None and epg.ac != ac: epg.ac = ac; mod = True
        if qvlan != None and epg.qvlan != qvlan: epg.qvlan = qvlan; mod = True
        if mod:
            epg.update()
            self.lock.on()
            for ep in self.eps[epg_dn].values(): self.inspect(epg, ep)
            self.lock.off()
        return epg
    
    def setMacIP(self, epg_dn, mac, ip, name=None):
        if epg_dn not in self.macips:
            macip = MacIP(epg_dn, mac, ip, name).create()
            self.macips[epg_dn] = {mac:macip}
        else:
            if mac not in self.macips[epg_dn]:
                macip = MacIP(epg_dn, mac, ip, name).create()
                self.macips[epg_dn][mac] = macip
            else:
                macip = self.macips[epg_dn][mac]
                if macip.ip != ip or macip.name != name:
                    macip.ip = ip
                    if name != None: macip.name = name
                    macip.update()
        self.lock.on()
        if epg_dn in self.epgs:
            epg = self.epgs[epg_dn]
            for ep in self.eps[epg_dn].values(): self.inspect(epg, ep)
        self.lock.off()
        return macip
    
    def delMacIP(self, epg_dn, mac):
        macip = self.macips[epg_dn].pop(mac)
        macip.delete()
        if not self.macips[epg_dn]: self.macips.pop(epg_dn)
        self.lock.on()
        if epg_dn in self.epgs:
            epg = self.epgs[epg_dn]
            for ep in self.eps[epg_dn].values(): self.inspect(epg, ep)
        self.lock.off()
        return macip
    
    def inspect(self, epg, ep):
        try:
            if epg.useg: self.blockVMDomainEP(epg, ep)
            else: self.blockPhysicalEP(epg, ep)
        except Exception as e: print str(e)
    
    def blockVMDomainEP(self, epg, ep):
        pass
    
    def blockPhysicalEP(self, epg, ep):
        if epg.ac:
            if not ep.deleted and not ep.blocked:
                if ep.epg_dn in self.macips and ep.mac in self.macips[ep.epg_dn] and ep.ip == self.macips[ep.epg_dn][ep.mac].ip: return
                self.createStaticEP(epg, ep)
                print 'B %s' % str(ep)
            elif ep.deleted and ep.blocked:
                self.deleteStaticEP(ep)
                print 'R %s' % str(ep)
            elif ep.blocked:
                if ep.epg_dn not in self.macips or ep.mac not in self.macips[ep.epg_dn] or ep.ip != self.macips[ep.epg_dn][ep.mac].ip: return
                self.deleteStaticEP(ep)
                print 'R %s' % str(ep)
        else:
            if ep.blocked:
                self.deleteStaticEP(ep)
                print 'R %s' % str(ep)
    
    def createStaticEP(self, epg, ep):
        if not ep.path_dn:
            try: path_dn = self.ctrl(ep.dn, detail=True).Class('fvRsCEpToPathEp').list(detail=True)[0]['tDn']
            except Exception as e: raise Exception('could not get EP Path with %s' % str(e))
        else: path_dn = ep.path_dn
        static_ep = {
            'fvStCEp' : {
                'attributes' : { 'mac' : ep.mac, 'encap' : 'vlan-%d' % epg.qvlan, 'type' : 'silent-host' },
                'children' : [{
                    'fvRsStCEpToPathEp' : { 'attributes' : { 'tDn' : path_dn } }
                }]
            }
        }
        try: self.ctrl.post('/api/mo/' + ep.epg_dn + '.json', json.dumps(static_ep))
        except Exception as e: raise Exception('could not create Static EP with %s' % str(e))
        ep.blocked = True
        ep.update()
    
    def deleteStaticEP(self, ep):
        static_ep_dn = ep.dn.replace('/cep-', '/stcep-') + '-type-silent-host'
        try: self.ctrl(static_ep_dn, detail=True).delete()
        except Exception as e: raise Exception('could not delete Static EP with %s' % str(e))
        ep.blocked = False
        ep.update()
