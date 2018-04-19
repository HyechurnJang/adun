# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 5.
@author: HyechurnJang
'''

import re
from pygics import rest
from model import EPG, EP, MacIP
from core import Tracker

tracker = Tracker('10.72.86.21', 'admin', '1234Qwer')

#===============================================================================
# Engine Rest API
#===============================================================================

def changeDNtoWN(dn): return dn.replace('/', '.')
def changeWNtoDN(url): return url.replace('.', '/')

# EPG
@rest('GET', '/epg')
def get_epg(req, id=None, epg_wn=None):
    try:
        if id != None: return EPG.get(int(id)).toDict()
        else:
            if epg_wn != None:
                epg_dn = changeWNtoDN(epg_wn)
                if epg_dn in tracker.epgs: return tracker.epgs[epg_dn].toDict()
            else: return [epg.toDict() for epg in tracker.epgs.values()]
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/epg')
def set_epg(req, id=None, epg_wn=None):
    try:
        if id != None: epg_dn = EPG.get(int(id)).dn
        elif epg_wn != None: epg_dn = changeWNtoDN(epg_wn)
        else: raise Exception('invalid parameter')
        ac = req.data['ac'] if 'ac' in req.data else None
        qvlan = int(req.data['qvlan']) if 'qvlan' in req.data else None
        return tracker.setEPGAC(epg_dn, ac, qvlan).toDict()
    except Exception as e: return {'error', str(e)}

# EP
@rest('GET', '/ep')
def get_ep(req, id=None, epg_wn=None):
    try:
        if id != None:
            ep = EP.get(int(id))
            ep_data = ep.toDict()
            if ep.epg_dn in tracker.macips and ep.mac in tracker.macips[ep.epg_dn]:
                macip = tracker.macips[ep.epg_dn][ep.mac]
                ep_data['name'] = macip.name
                ep_data['mapped'] = macip.id
            else:
                ep_data['name'] = ''
                ep_data['mapped'] = 0
            return ep_data
        else:
            result = []
            if epg_wn != None:
                epg_dn = changeWNtoDN(epg_wn)
                if epg_dn in tracker.eps:
                    for ep in tracker.eps[epg_dn].values():
                        ep_data = ep.toDict()
                        if ep.epg_dn in tracker.macips and ep.mac in tracker.macips[ep.epg_dn]:
                            macip = tracker.macips[ep.epg_dn][ep.mac]
                            ep_data['name'] = macip.name
                            ep_data['mapped'] = macip.id
                        else:
                            ep_data['name'] = ''
                            ep_data['mapped'] = 0
                        result.append(ep_data)
            else:
                for epg in tracker.eps.values():
                    for ep in epg.values():
                        ep_data = ep.toDict()
                        if ep.epg_dn in tracker.macips and ep.mac in tracker.macips[ep.epg_dn]:
                            macip = tracker.macips[ep.epg_dn][ep.mac]
                            ep_data['name'] = macip.name
                            ep_data['mapped'] = macip.id
                        else:
                            ep_data['name'] = ''
                            ep_data['mapped'] = 0
                        result.append(ep_data)
            return result
    except Exception as e: return {'error', str(e)}

# MacIP
@rest('GET', '/macip')
def get_macip(req, id=None, epg_wn=None):
    try:
        if id != None: return MacIP.get(int(id)).toDict()
        else:
            result = []
            if epg_wn != None:
                epg_dn = changeWNtoDN(epg_wn)
                if epg_dn in tracker.macips:
                    for macip in tracker.macips[epg_dn].values(): result.append(macip.toDict())
            else:
                for epg in tracker.macips.values():
                    for macip in epg.values(): result.append(macip.toDict())
            return result
    except Exception as e: return {'error', str(e)}

@rest('POST', '/macip')
def set_macip(req, id=None, epg_wn=None):
    try:
        if id != None: epg_dn = MacIP.get(int(id)).epg_dn
        elif epg_wn != None: epg_dn = changeWNtoDN(epg_wn)
        else: raise Exception('invalid parameter')
        mac = req.data['mac']
        ip = req.data['ip']
        name = req.data['name'] if 'name' in req.data else None
        return tracker.setMacIP(epg_dn, mac, ip, name).toDict()
    except Exception as e: return {'error' : str(e)}

@rest('DELETE', '/macip')
def del_macip(req, id):
    try:
        macip = MacIP.get(int(id))
        return tracker.delMacIP(macip.epg_dn, macip.mac).toDict()
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/hist/epg')
def get_epg_history(req):
    try: return [epg.toDict() for epg in EPG.list()]
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/hist/ep')
def get_ep_history(req):
    try: return [ep.toDict() for ep in EP.list()]
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/topo/epg')
def get_epg_topology(req):
    topo = {}
    
    for epg in tracker.epgs.values():
        kv = re.match('uni/tn-(?P<tn>[\W\w]+)/ap-(?P<ap>[\W\w]+)/epg-(?P<epg>[\W\w]+)', epg.dn)
        if kv:
            rn_tn = kv.group('tn')
            rn_ap = kv.group('ap')
            rn_epg = kv.group('epg')
            if rn_tn not in topo: topo[rn_tn] = {}
            if rn_ap not in topo[rn_tn]: topo[rn_tn][rn_ap] = {}
            if rn_epg not in topo[rn_tn][rn_ap]: topo[rn_tn][rn_ap][rn_epg] = epg
    
    aci_children = []
    aci = {'name' : 'ACI', 'type' : 'aci', 'children' : aci_children}
    for tn_name, tn in topo.items():
        tn_children = []
        tn_data = {'name' : tn_name, 'type' : 'tn', 'children' : tn_children}
        for ap_name, ap in tn.items():
            ap_children = []
            ap_data = {'name' : ap_name, 'type' : 'ap', 'children' : ap_children}
            for epg_name, epg in ap.items():
                epg_data = {
                    '_id' : epg.id,
                    'id' : 'topo-epg-%d' % epg.id,
                    'type' : 'epg',
                    'name' : epg_name,
                    'dn' : epg.dn,
                    'wn' : changeDNtoWN(epg.dn),
                    'ac' : epg.ac,
                    'useg' : epg.useg,
                    'qvlan' : epg.qvlan,
                    'epcount' : len(tracker.eps[epg.dn])
                }
                ap_children.append(epg_data)
            tn_children.append(ap_data)
        aci_children.append(tn_data)
    
    return aci
            
@rest('GET', '/topo/ep')
def get_ep_topology(req, epg_wn):
    result = []
    epg_dn = changeWNtoDN(epg_wn)
    if epg_dn in tracker.eps:
        for ep in tracker.eps[epg_dn].values():
            ep_data = ep.toDict()
            if ep.epg_dn in tracker.macips and ep.mac in tracker.macips[ep.epg_dn]:
                macip = tracker.macips[ep.epg_dn][ep.mac]
                ep_data['name'] = '[%s] %s / %s' % (macip.name, ep.mac, ep.ip) if macip.name else '%s / %s' % (ep.mac, ep.ip)
                ep_data['mapped'] = macip.id
            else:
                ep_data['name'] = '%s / %s' % (ep.mac, ep.ip)
                ep_data['mapped'] = 0
            ep_data['_id'] = ep_data['id']
            ep_data['id'] = 'topo-ep-%d' % ep_data['id']
            ep_data['type'] = 'ep'
            result.append(ep_data)
    return result
