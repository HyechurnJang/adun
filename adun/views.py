# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 2.
@author: HyechurnJang
'''

import re
import json
from django import forms
from django.shortcuts import render, redirect
from django.http import JsonResponse
from api import engine

#===============================================================================
# HTML Pages
#===============================================================================
def main(request):
    
    class Form(forms.Form):
        epg_id = forms.IntegerField(widget=forms.HiddenInput())
        epg_ac = forms.BooleanField(required=False, widget=forms.CheckboxInput())
        epg_qvlan = forms.IntegerField(widget=forms.TextInput())
        
        def clean(self):
            self.epg_id = self.cleaned_data.get('epg_id')
            self.epg_ac = self.cleaned_data.get('epg_ac', False)
            self.epg_qvlan = self.cleaned_data.get('epg_qvlan')
            return self.cleaned_data
    
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid(): engine.setEPG(form.epg_id, form.epg_ac, form.epg_qvlan)
        return redirect('main')
    
    return render(request, 'main.html', {'form' : Form()})

def curr_epg(request):
    modal_button = '<div class="btn-epg-option-wrap"><button type="button" class="btn btn-outline-primary btn-epg-option" data-toggle="modal" data-target="#set-epg-option" epg_id="%d" epg_qvlan="%d" epg_ac="%s" onclick="set_epg_option_value($(this));">Option</button></div>'
    data = [[
        epg['dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
        'uSegment' if epg['useg'] == 'yes' else 'QVlan-%d' % epg['qvlan'],
        'Enforced' if epg['ac'] else ' ',
        modal_button % (epg['id'], epg['qvlan'], str(epg['ac']).lower())
    ] for epg in engine.getEPG()]
    return JsonResponse({'data' : data})

def curr_ep(request):
    data = []
    for epg in engine.getEP().values():
        for ep in epg:
            data.append([
                ep['epg_dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
                ep['path_dn'],
                ep['mac'],
                ep['ip'],
                ep['status'],
                ep['tstamp'],
                'Blocked' if ep['blocked'] else ' ',
            ])
    return JsonResponse({'data' : data})

def hist(request): return render(request, 'hist.html')

def hist_epg(request):
    data = [[
        epg['tstamp'],
        epg['status'],
        epg['dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
    ] for epg in engine.getEPGHist()]
    return JsonResponse({'data' : data})

def hist_ep(request):
    data = [[
        ep['tstamp'],
        ep['status'],
        ep['epg_dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
        ep['mac'],
        ep['ip']
    ] for ep in engine.getEPHist()]
    return JsonResponse({'data' : data})

def macip(request, accept=None, crud=None, macip_id=None):
    
    class CreateForm(forms.Form):
        macip_tn = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        macip_ap = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        macip_epg = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        macip_mac = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        macip_ip = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
        macip_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
        
        def clean(self):
            self.macip_tn = self.cleaned_data.get('macip_tn')
            if not self.macip_tn: raise forms.ValidationError('invalid parameter')
            self.macip_ap = self.cleaned_data.get('macip_ap')
            if not self.macip_ap: raise forms.ValidationError('invalid parameter')
            self.macip_epg = self.cleaned_data.get('macip_epg')
            if not self.macip_epg: raise forms.ValidationError('invalid parameter')
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
    
    class UpdateForm(forms.Form):
        update_macip_name = forms.CharField(required=False, widget=forms.HiddenInput())
        update_macip_mac = forms.CharField(widget=forms.HiddenInput())
        update_macip_ip = forms.CharField(widget=forms.HiddenInput())
        
        def clean(self):
            self.macip_name = self.cleaned_data.get('update_macip_name', None)
            self.macip_mac = self.cleaned_data.get('update_macip_mac')
            if not self.macip_mac: raise forms.ValidationError('invalid parameter')
            if re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', self.macip_mac) == None:
                raise forms.ValidationError('invalid mac address')
            self.macip_ip = self.cleaned_data.get('update_macip_ip')
            if not self.macip_ip: raise forms.ValidationError('invalid parameter')
            if re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', self.macip_ip) == None:
                raise forms.ValidationError('invalid ip address')
            return self.cleaned_data
    
    if request.method == 'GET' and accept == 'json':
        option_button = '''
<div class="btn-macip-option-wrap"><div class="btn-group" role="group">
<button type="button" class="btn btn-outline-primary btn-macip-option" macip_id="%d" onclick="update_macip($(this));">
Update
</button>
<button type="button" class="btn btn-outline-danger btn-macip-option" macip_id="%d" onclick="delete_macip($(this));">
Delete
</button>
</div></div>
        '''
        data = []
        for epg in engine.getMacIP().values():
            for macip in epg:
                macip_id = macip['id']
                data.append([
                    macip['epg_dn'].replace('uni/tn-', '').replace('/ap-', ' / ').replace('/epg-', ' / '),
                    '<input type="text" id="macip-name-%d" value="%s">' % (macip_id, macip['name']),
                    '<input type="text" id="macip-mac-%d" value="%s">' % (macip_id, macip['mac']),
                    '<input type="text" id="macip-ip-%d" value="%s">' % (macip_id, macip['ip']),
                    option_button % (macip_id, macip_id)
                ])
        return JsonResponse({'data' : data})
    
    if request.method == 'POST':
        if crud == 'create':
            form = CreateForm(request.POST)
            if form.is_valid():
                engine.setMacIPwithDN(form.macip_tn, form.macip_ap, form.macip_epg, form.macip_mac, form.macip_ip, form.macip_name)
        elif crud == 'update':
            form = UpdateForm(request.POST)
            if form.is_valid():
                engine.setMacIPwithID(int(macip_id), form.macip_mac, form.macip_ip, form.macip_name)
        elif crud == 'delete':
            engine.delMacIP(int(macip_id))
        return redirect('macip')
    
    return render(request, 'macip.html', {'form' : CreateForm()})
