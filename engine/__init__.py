# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 5.
@author: HyechurnJang
'''

from pygics import rest
from model import EPG, EP, MacIP
from core import Tracker

tracker = Tracker('10.72.86.21', 'admin', '1234Qwer')

#===============================================================================
# Engine Rest API
#===============================================================================
@rest('GET', '/epg')
def get_epg(req, id=None):
    if id != None:
        try: return EPG.get(id).toDict()
        except Exception as e: return {'error' : str(e)}
    else:
        result = []
        for epg in tracker.epgs.values(): result.append(epg.toDict())
        return result

@rest('POST', '/epg')
def set_epg(req, id=None):
    if id != None:
        try: epg_dn = EPG.get(id).dn
        except Exception as e: return {'error', str(e)}
    else:
        try: epg_dn = 'uni/tn-%s/ap-%s/epg-%s' % (req.data['tn'], req.data['ap'], req.data['epg'])
        except: return {'error' : 'invalid parameter'}
    try:
        ac = req.data['ac'] if 'ac' in req.data else None
        qvlan = int(req.data['qvlan']) if 'qvlan' in req.data else None
    except: return {'error' : 'invalid parameter'}
    try: return tracker.setEPGAC(epg_dn, ac, qvlan).toDict()
    except Exception as e: return {'error', str(e)}

@rest('GET', '/hist/epg')
def get_epg_history(req):
    return [epg.toDict() for epg in EPG.list()]

@rest('GET', '/ep')
def get_ep(req, id=None):
    if id != None:
        try: return EP.get(id).toDict()
        except Exception as e: return {'error' : str(e)}
    else:
        result = {}
        for epg_dn, epg in tracker.eps.items():
            result[epg_dn] = []
            for ep in epg.values():
                result[epg_dn].append(ep.toDict())
        return result

@rest('GET', '/hist/ep')
def get_ep_history(req):
    return [ep.toDict() for ep in EP.list()]

@rest('GET', '/macip')
def get_macip(req, id=None):
    if id != None:
        try: return MacIP.get(id).toDict()
        except Exception as e: return {'error' : str(e)}
    else:
        result = {}
        for epg_dn in tracker.macips:
            result[epg_dn] = []
            for macip in tracker.macips[epg_dn].values():
                result[epg_dn].append(macip.toDict())
        return result

@rest('POST', '/macip')
def set_macip(req, id=None):
    if id != None:
        try: epg_dn = MacIP.get(id).epg_dn
        except Exception as e: return {'error' : str(e)}
    else:
        try: epg_dn = 'uni/tn-%s/ap-%s/epg-%s' % (req.data['tn'], req.data['ap'], req.data['epg'])
        except: return {'error' : 'invalid parameter'}
    try:
        mac = req.data['mac']
        ip = req.data['ip']
        name = req.data['name'] if 'name' in req.data else None
    except: return {'error' : 'invalid parameter'}
    try: return tracker.setMacIP(epg_dn, mac, ip, name).toDict()
    except Exception as e: return {'error' : str(e)}

@rest('DELETE', '/macip')
def del_macip(req, id):
    try: macip = MacIP.get(id)
    except Exception as e: return {'error' : str(e)}
    try: return tracker.delMacIP(macip.epg_dn, macip.mac).toDict()
    except Exception as e: return {'error' : str(e)}
