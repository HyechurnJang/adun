# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 2.
@author: HyechurnJang
'''

import re
import json
from django import forms
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from api import engine

#===============================================================================
# HTML Pages
#===============================================================================

class EPGForm(forms.Form):
    epg_id = forms.IntegerField(widget=forms.HiddenInput())
    epg_ac = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    epg_qvlan = forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control form-control-sm'}))
    
    def clean(self):
        self.epg_id = self.cleaned_data.get('epg_id')
        self.epg_ac = self.cleaned_data.get('epg_ac', False)
        self.epg_qvlan = self.cleaned_data.get('epg_qvlan')
        return self.cleaned_data

class MacIPForm(forms.Form):
    macip_mac = forms.CharField(widget=forms.TextInput())
    macip_ip = forms.CharField(widget=forms.TextInput())
    macip_name = forms.CharField(required=False, widget=forms.TextInput())
      
    def clean(self):
        self.macip_mac = self.cleaned_data.get('macip_mac')
        if not self.macip_mac: raise forms.ValidationError('invalid parameter')
        if re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', self.macip_mac) == None:
            raise forms.ValidationError('invalid mac address')
        self.macip_ip = self.cleaned_data.get('macip_ip')
        if not self.macip_ip: raise forms.ValidationError('invalid parameter')
        if re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', self.macip_ip) == None:
            raise forms.ValidationError('invalid ip address')
        self.macip_name = self.cleaned_data.get('macip_name', None)
        return self.cleaned_data

def main(request):
    return render(request, 'main.html', {
        'epg_form' : EPGForm(),
        'macip_form' : MacIPForm(),
    })

def topo(request, target, ident=None):
    if request.method == 'GET':
        if target == 'epg': return JsonResponse({'data' : engine.getEPGTopo()})
        elif target == 'ep': return JsonResponse({'data' : engine.getEPTopo(ident)})
    return redirect('main')

def epg_ep(request, ident):
    if request.method == 'GET':
        data = [[
            ep['mac'],
            ep['ip'],
            'Blocked' if ep['blocked'] else ' '
        ] for ep in engine.getEP(epg_wn=ident)]
        return JsonResponse({'data' : data})
    return redirect('main')

@csrf_exempt
def epg_macip(request, ident, crud):
    ret = False
    if request.method == 'GET' and crud == 'read':
        option_button = '''
<div class="btn-epg-detail-macip-wrap"><div class="btn-group" role="group">
<button type="button" class="btn btn-outline-info btn-epg-update-macip" onclick="updateMacIP(%d);">
Update
</button>
<button type="button" class="btn btn-outline-danger btn-epg-delete-macip" onclick="deleteMacIP(%d);">
Delete
</button>
</div></div>
        '''
        data = [[
            '<input type="text" class="input-epg-detail-macip" id="epg-update-macip-name-%d" value="%s">' % (macip['id'], macip['name']),
            '<input type="text" class="input-epg-detail-macip" id="epg-update-macip-mac-%d" value="%s">' % (macip['id'], macip['mac']),
            '<input type="text" class="input-epg-detail-macip" id="epg-update-macip-ip-%d" value="%s">' % (macip['id'], macip['ip']),
            option_button % (macip['id'], macip['id'])
        ] for macip in engine.getMacIP(epg_wn=ident)]
        return JsonResponse({'data' : data})
    
    elif request.method == 'POST':
        form = MacIPForm(request.POST)
        if form.is_valid():
            if crud == 'create':
                ret = engine.setMacIPwithWN(ident, form.macip_mac, form.macip_ip, form.macip_name)
            elif crud == 'update':
                ret = engine.setMacIPwithID(int(ident), form.macip_mac, form.macip_ip, form.macip_name)
    
    elif request.method == 'DELETE' and crud == 'delete':
        ret = engine.delMacIP(int(ident))
    
    return JsonResponse({'data' : ret})

def epg_setting(request):
    if request.method == 'POST':
        form = EPGForm(request.POST)
        if form.is_valid(): engine.setEPG(form.epg_id, form.epg_ac, form.epg_qvlan)
    return redirect('main')






# def hist(request): return render(request, 'hist.html')
# 
# def hist_epg(request):
#     data = [[
#         epg['tstamp'],
#         epg['status'],
#         epg['dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
#     ] for epg in engine.getEPGHist()]
#     return JsonResponse({'data' : data})
# 
# def hist_ep(request):
#     data = [[
#         ep['tstamp'],
#         ep['status'],
#         ep['epg_dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
#         ep['mac'],
#         ep['ip']
#     ] for ep in engine.getEPHist()]
#     return JsonResponse({'data' : data})


