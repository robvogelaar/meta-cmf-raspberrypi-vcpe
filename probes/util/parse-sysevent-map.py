#!/usr/bin/env python3

import sys, stat, os, re, errno, json, math, datetime, subprocess, hashlib
from optparse import OptionParser


readme = '''\
left panel:
Utopia Service Map
all services with a grouping / coloring
for each service lists the service handler(s), the async tuple(s) and the default '-status' value tuple
async_tuples with a larger font are triggered in multiple service(s) handlers
async_tuples with a grey background were never triggered
hover for more info

Utopia Async Registrations
which clients register for which async notifications
which clients register for which async actions

Utopia Async Invokations
which clients invoke which async notifications
which clients invoked which async actions

right panel:
debug..
all 'raw' debug events collected from syseventd debug output in order of occurence
set..
all tuples set's (to a value) by a client (in red) in order of occurrence
get..
all tuples get's (and value returned) by a client (in red) in order of occurrence
run_external_executable..
all invokations of async tuples (async actions) in order of occurrence
send_notification..
all notifications of async tuples (async messages) in order of occurrence
clients..
all client handle names with the original client application binary
tuples..
all tuples with _all_ of its set values and option values

'''


client_mappings = '''
ccsp_wifi_agent:/usr/lib/libCcspWifiAgent_sbapi
CcspEthAgent:usr/bin/CcspEthAgent
CcspTandDSsp:/usr/lib/libLowLatency.so
cisco-gre-dm:/usr/lib/libtr181.so.0.0.0 ccsp-p-and-m
cm_gw_prov:/usr/bin/CcspCMAgentSsp
common_master:/usr/lib/libtr181.so.0.0.0 ccsp-p-and-m
dhcp_evt_handler:/usr/lib/libdhcp_client_utils.so
firewall:/usr/bin/firewall
GenFWLog:/usr/bin/GenFWLog
get_from_manageable_device:/usr/bin/CcspLMLite
gw_prov-gs:/usr/bin/gw_prov_utopia
gw_prov:/usr/bin/gw_prov_utopia
gw_prov_ethwan-gs:/usr/bin/gw_prov_ethwan
gw_prov_ethwan:/usr/bin/gw_prov_ethwan
handle_sw:/usr/bin/service_multinet_exec
hotspotfd-update:/usr/bin/CcspHotspot
meshAgent-gs:/usr/bin/meshAgent
meshAgent:/usr/bin/meshAgent
multinet_ev:/usr/bin/service_multinet_exec
netmonitor:usr/bin/netmonitor
profileHunter:/usr/bin/profileHunter
profilehunter:/usr/bin/profileHunter
rdkb_cm_hal-gs:/usr/lib/libcm_mgnt.so
rdkb_cm_hal:/usr/lib/libcm_mgnt.so
rdkb_mta_hal-gs:/usr/lib/libhal_mta.so
rdkb_mta_hal:/usr/lib/libhal_mta.so
sect1:/usr/lib/libutctx.so
sectl:/usr/bin/sysevent
SERVICE-DDNS:/usr/bin/service_ddns
SERVICE-DSLITE:/usr/bin/service_dslite
SERVICE-IPV6:/usr/bin/service_ipv6
SERVICE-ROUTED:/usr/bin/service_routed
SERVICE-WAN:/usr/bin/service_wan
service_ddns:/usr/bin/service_ddns
service_dhcp:/usr/bin/service_dhcp
service_dhcpv6_client:/usr/bin/service_dhcpv6_client
sysevent dhcpv6:/usr/bin/sysevent
Interface_evt_handler:/usr/lib/libtr181.so
srvmgr:/usr/lib/libsrvmgr.so
dhcpv6:/usr/lib/libtr181.so.0.0.0
system_default_set:/usr/bin/apply_system_defaults
tr069:/usr/bin/CcspTr069PaSsp
trigger:/usr/bin/trigger
udhcpc:/usr/bin/service_udhcpc
utapi:/usr/lib/libutapi.so
vlanmgr:/usr/bin/VlanManager
voip:/usr/bin/telcovoice_manager
voip_notify:usr/bin/telcovoice_manager
WAN State:ccsp-mta-agent
wan_connectivity_check:/usr/lib/libdmltad.so
wan_connectivity_check_sysevent_mntr:/usr/lib/libdmltad.so
wanmanager:/usr/bin/wanmanager
wanmgr:/usr/bin/wanmanager
wifi_agent:/usr/lib/libwifi.so
wifiMonitor:/usr/lib/libwifi.so'''

def rgb_to_y(r, g, b):

    y = 0.30*r + 0.59*g + 0.11*b
    #i = 0.60*r - 0.28*g - 0.32*b
    #q = 0.21*r - 0.52*g + 0.31*b
    return y


def greylevel(hexcolor):

    t = tuple([int(hexcolor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)])
    return int(rgb_to_y(*t))


def getcontrastcolor(color):

    if greylevel(color) < 128:
        return 'white'
    else:
        return 'black'


def getcolor(s, n):

    #https://www.w3schools.com/colors/colors_monochromatic.asp

    monochromatic = [
    '#FFDEDB', '#FE8176', '#FE2712', '#A70F01', '#340D09',
    '#FFE2DC', '#FE8F77', '#FD3A0F', '#A72002', '#341109',
    '#FFE5DC', '#FE9772', '#FD4D0C', '#A22C02', '#341509',
    '#FFE8DC', '#FE9F6D', '#FC600A', '#9D3802', '#341809',
    '#FFEBDC', '#FEAB6D', '#FC7307', '#9D4502', '#341C09',
    '#FEEEDC', '#FDB768', '#FB8604', '#975102', '#342009',
    '#FFF1DC', '#FDC168', '#FB9902', '#975B02', '#342309',
    '#FEF3DC', '#FDCD6D', '#FBA90A', '#9C6902', '#342609',
    '#FFF5DC', '#FED777', '#FCBA12', '#A77802', '#342809',
    '#FEF7DC', '#FDE281', '#FCCB1A', '#B08A03', '#342B09',
    '#FFF9DC', '#FEEC86', '#FDDC22', '#B69B02', '#342E09',
    '#FFFCDC', '#FEF590', '#FDED2A', '#C0B002', '#343009',
    '#FFFFDB', '#FEFE9A', '#FEFE33', '#CBCB01', '#343409',
    '#FBFDDE', '#F1F791', '#E4F132', '#A5B00C', '#313409',
    '#F7FBDF', '#E3F08E', '#CBE432', '#8C9E15', '#2E3409',
    '#F4F9E1', '#D3E788', '#B2D732', '#71881B', '#2B3409',
    '#F1F8E2', '#C0DF81', '#98CA32', '#59761E', '#263409',
    '#EEF8E3', '#B0DC7A', '#7FBD32', '#496D1D', '#213409',
    '#EBF7E3', '#9BD770', '#66B032', '#375F1B', '#1B3409',
    '#E8F3E8', '#92C591', '#559E54', '#305A30', '#0A3409',
    '#E7F3EF', '#79BEA8', '#448D76', '#23483C', '#093426',
    '#E4F1F6', '#67AFCB', '#347B98', '#1A3E4C', '#092834',
    '#E1ECF9', '#609CE1', '#236AB9', '#133863', '#091D34',
    '#DEE9FC', '#6395F2', '#1258DC', '#0A337F', '#091834',
    '#DBE5FF', '#678FFE', '#0247FE', '#012998', '#091534',
    '#DDE3FD', '#798EF6', '#183BF0', '#0A2299', '#091034',
    '#E0E0FB', '#8A8AEF', '#2E2FE3', '#151599', '#090934',
    '#E5E0FA', '#8C78E8', '#4424D6', '#29157E', '#110934',
    '#E9DFFB', '#905BEC', '#5A18C9', '#300D6E', '#190934',
    '#EFDDFD', '#A33AF2', '#700CBC', '#36065B', '#210934',
    '#F7DBFF', '#C91BFE', '#8601AF', '#3A004C', '#2A0934',
    '#FDDDFC', '#F415ED', '#9A0794', '#3A0339', '#340933',
    '#FDDEF3', '#F033B4', '#AE0D7A', '#510639', '#340926',
    '#FCDFEB', '#ED5094', '#C21460', '#660B32', '#34091C',
    '#FBDFE6', '#EC6988', '#D61A46', '#7B0F28', '#340913',
    '#FCDEE0', '#F37C84', '#EA202C', '#950E17', '#34090C',
    ]


    #0 .. 35
    red = 0
    orange = 6
    yellow = 12
    green = 18
    blue = 24
    purple = 30

    majorcolor = blue

    if 'clients' in s:
        majorcolor = green + 1

    if 'notifications' in s:
        majorcolor = green + 2

    if 'actions' in s:
        majorcolor = green + 3


    elif s in ['mcastproxy','mldproxy', 'igd', 'radiusrelay']:
        majorcolor = yellow

    elif s in ['forwarding','bridge']:
        majorcolor = yellow


    elif s in ['lan', 'wan']:
        majorcolor = green

    elif s in ['ipv4', 'ipv6']:
        majorcolor = green

    elif s in ['multinet']:
        majorcolor = green

    elif s in ['dhcp_server', 'dhcpv6_client']:
        majorcolor = green



    elif s in ['crond', 'cosa', 'potd']:
        majorcolor = red

    elif s in ['misc','ntpd', 'sshd']:
        majorcolor = red



    return monochromatic[majorcolor * 5 + n]


def hash(s):
    return '_' + hashlib.md5((s).encode()).hexdigest()


def group(services, items, params, prepend):

    sn = []
    for s in services:
        sn.append(s['name'])

    items = [value for value in items if value in sn]

    dot = ''
    i = 0
    while i < len(items) - 1:
        dot += '%s -> %s%s;\n' %(hash(prepend + items[i]), hash(prepend + items[i + 1]), params)
        i+= 1

    return dot


def gen_dot_service_map(clients, services, tples, async_actions, async_messages):

    dot = ''
    dot += 'digraph {\n'
    dot += 'bgcolor=lightcyan\n'
    dot += 'rankdir=LR\n'
    dot += 'nodesep=0\n'
    dot += 'ranksep=\"0.5\"\n'

    dot += 'fontname="Arial"; fontsize=16; fontcolor=grey\n'
    dot += 'label="Utopia Service Map"\n'
    dot += 'labelloc=top\n'
    dot += 'labeljust="l"\n'
    dot += 'edge [color=black arrowsize=0.5 penwidth=0.1]\n'


    multi_subjects = []
    tmp_subjects = []

    for s in services:
        #print(s['name'])
        for subject in s['subjects']:
            if subject.split(':')[0] not in tmp_subjects:
                tmp_subjects.append(subject.split(':')[0])
            else:
                if subject.split(':')[0] not in multi_subjects:
                    multi_subjects.append(subject.split(':')[0])

    #print(multi_subjects)


    #services

    #for s in services:
    for s in sorted(services, key=lambda x: x['name']):


        service_name = s['name']

        dot += 'subgraph cluster' + hash(service_name) + ' {\n'
        dot += 'labeljust=""\n'

        dot += 'margin=3;\n'
        dot += 'penwidth=1.1;\n'
        dot += 'shape=plaintext;\n'
        dot += 'fillcolor=\"%s\";\n' %getcolor(service_name, 0)
        dot += 'color=\"%s\";\n' %getcolor(service_name, 3)
        dot += 'fontcolor=\"%s\";\n' %getcolor(service_name, 3)
        dot += 'fontsize=10;\n'
        dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
        dot += 'label=\"' + service_name + '\\r\";\n'
        #dot += 'label=\"' + service_name + '\";\n'
        dot += 'style=\"filled, rounded\";\n'

        dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('service_' + service_name)


        for function_name in s['functions']:

            dot += 'subgraph cluster' + hash(function_name) + ' {\n'

            dot += 'margin=3;\n'
            dot += 'penwidth=0.5;\n'
            dot += 'fillcolor=\"%s\";\n' %getcolor(service_name, 1)
            dot += 'color=\"%s\";\n' %getcolor(service_name, 3)
            dot += 'fontcolor=\"%s\";\n' %getcolor(service_name, 3)
            dot += 'fontsize=8;\n'
            dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
            dot += 'label=\"' + function_name.split('/')[-1] + '\\l' + '\";\n'
            dot += 'style=\"filled, rounded\";\n'
            dot += 'tooltip=\"%s\";\n' %function_name

            dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash(function_name)

            maxlen = 0
            for subject in s['subjects']:
                subject_name = subject.split(':')[0]
                if subject.split(':')[1] == function_name:
                    if len(subject_name) > maxlen:
                        maxlen = len(subject_name)

            for subject in s['subjects']:

                subject_name = subject.split(':')[0]

                if subject.split(':')[1] == function_name:

                    fontsize=8
                    style='filled'
                    label=subject_name
                    if subject_name in multi_subjects:
                        #label+= ' * '
                        fontsize = 10
                    label+='\\l'

                    width = maxlen / 16
                    shape='box'

                    v = []
                    for t in tples:
                        if t['subject'] == subject_name:
                            v = t['values']
                            break

                    if v:
                        fillcolor=getcolor(service_name, 2)
                        color=getcolor(service_name, 4)
                        fontcolor=getcontrastcolor(getcolor(service_name, 2))
                    else:
                        fillcolor='lightgrey'
                        color='grey'
                        fontcolor=getcolor(service_name, 2)

                    tooltip=subject_name
                    if v:
                        tooltip += '\n\n'
                        for v in t['values']:
                            tooltip += '\'' + v.split(':')[0] + '\'' + '<-' + v.split(':')[1] + '\n'
                    else:
                        tooltip += '\n\n' + '<none>'


                    url=''

                    dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
                    % (hash('subject_' + function_name + '_' + subject_name), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)


            dot += '}\n'




            dot += 'subgraph cluster' + hash(service_name + '-status') + ' {\n'

            dot += 'margin=3;\n'
            dot += 'penwidth=0.5;\n'
            dot += 'fillcolor=\"%s\";\n' %getcolor(service_name, 0)
            dot += 'color=\"%s\";\n' %getcolor(service_name, 0)
            dot += 'fontcolor=\"%s\";\n' %getcolor(service_name, 3)
            dot += 'fontsize=8;\n'
            dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
            dot += 'label=\"\";\n'
            dot += 'style=\"filled, rounded\";\n'

            fontsize=8
            width=1.1
            shape='box'
            fillcolor=getcolor(service_name, 0)
            color=getcolor(service_name, 4)
            fontcolor=getcontrastcolor(getcolor(service_name, 0))

            tooltip=service_name + '-status'

            for t in tples:
                if t['subject'] == service_name + '-status':
                    tooltip += '\n'
                    for v in t['values']:
                        tooltip += '\n' + '\'' + v.split(':')[0] + '\'' + '<-' + v.split(':')[1]
                    break

            url=''

            dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
            % (hash(service_name + '-status'), service_name + '-status', fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)


            dot += '}\n'



        dot += '}\n'



    dot += group(services, ['forwarding','bridge','mldproxy','mcastproxy','igd', 'radiusrelay'], '[style=invisible arrowhead=none]', 'service_')
    dot += group(services, ['cosa','potd','crond', 'sshd','ntpd','misc'], '[style=invisible arrowhead=none]', 'service_')
    dot += group(services, ['lan','dhcp_server','multinet','ipv4','wan', 'ipv6','dhcpv6_client'], '[style=invisible arrowhead=none]', 'service_')
    dot += group(services, ['firewall','service_ddns', 'routed','hotspot','ccsphs'], '[style=invisible arrowhead=none]', 'service_')



    '''
    for ms in multi_subjects:
        mss = []
        for s in services:
            for subject in s['subjects']:
                if subject.split(':')[0] in ms:
                    mss.append(subject.split(':')[1] + '_' + subject.split(':')[0])
        dot+= group(mss, '', 'subject_')
    '''


    dot += '}\n'


    with open('service_map.dot', 'w') as f:
        for l in dot.splitlines():
            print(l, file = f)

    return dot




def gen_dot_async_registrations(clients, services, tples, async_messages):

    dot = ''
    dot += 'digraph {\n'
    dot += 'bgcolor=lightcyan\n'
    dot += 'rankdir=LR\n'
    dot += 'nodesep=0\n'
    dot += 'ranksep=\"2.5\"\n'

    dot += 'fontname="Arial"; fontsize=16; fontcolor=grey\n'
    dot += 'label="Utopia Async Registrations"\n'
    dot += 'labelloc=top\n'
    dot += 'labeljust="l"\n'
    dot += 'edge [color=black arrowsize=0.5 penwidth=0.1]\n'




    # notifications

    dot += 'subgraph cluster' + hash('notifications') + ' {\n'

    dot += 'margin=3;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('notifications', 1)
    dot += 'color=\"%s\";\n' %getcolor('notifications', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('notifications', 3)
    dot += 'fontsize=10;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
    dot += 'label=\"' + 'notifications' + '\\l' + '\";\n'
    dot += 'style=\"filled, rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')

    for a in sorted(async_messages, key=lambda x: x.split('|')[1]):

        notification = a.split('|')[1]

        label=notification+'\\l'
        fontsize=8
        style='filled'
        width=0
        shape='box'
        fillcolor=getcolor('notifications', 2)
        color=getcolor('notifications', 4)
        fontcolor=getcontrastcolor(getcolor('notifications', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('notification_' + notification), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'



    # clients

    m = {}
    for c in client_mappings.splitlines():
        if c:
            #print('[' + c + ']')
            m[c.split(':')[0]] = c.split(':')[1]

    dot += 'subgraph cluster' + hash('clients') + ' {\n'

    dot += 'margin=6;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('clients', 1)
    dot += 'color=\"%s\";\n' %getcolor('clients', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('clients', 3)
    dot += 'fontsize=14;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=\"0.1\" penwidth=0.1];\n'
    dot += 'label=\"' + 'clients' + '\\l' + '\";\n'
    dot += 'style=\"filled, rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')


    #sys.stderr.write("m=%s\n" %str(m))


    for client in clients:

        #sys.stderr.write("client=%s\n" %str(client))

        label=m[client] + '\n' + '\'' + client + '\''
        fontsize=12
        style='filled,rounded'
        width=0
        height=10
        shape='box'
        fillcolor=getcolor('clients', 2)
        color=getcolor('clients', 4)
        fontcolor=getcontrastcolor(getcolor('clients', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('client_' + client), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'





    # actions

    dot += 'subgraph cluster' + hash('actions') + ' {\n'

    dot += 'margin=3;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('actions', 1)
    dot += 'color=\"%s\";\n' %getcolor('actions', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('actions', 3)
    dot += 'fontsize=10;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
    dot += 'label=\"' + 'actions' + '\\l' + '\";\n'
    dot += 'style=\"filled, rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')

    for a in sorted(async_actions, key=lambda x: x.split('|')[1]):

        action = a.split('|')[1]

        label=action+'\\l'
        fontsize=8
        style='filled'
        width=0
        shape='box'
        fillcolor=getcolor('actions', 2)
        color=getcolor('actions', 4)
        fontcolor=getcontrastcolor(getcolor('actions', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('action_' + action), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'



    duplicates = []
    for a in sorted(async_messages, key=lambda x: x.split('|')[1]):
        connection = '%s -> %s[arrowhead=none];\n' %(hash('client_' + a.split('|')[2]), hash('notification_' + a.split('|')[1]))
        if connection not in duplicates:
            dot += connection
            duplicates.append(connection)


    for a in sorted(async_actions, key=lambda x: x.split('|')[1]):
        if a.split('|')[3] == 'srvmgr':
            color = 'grey'
        else:
            color = 'red'
        connection = '%s -> %s[arrowhead=none color=%s];\n' %(hash('action_' + a.split('|')[1]), hash('client_' + a.split('|')[3]), color)
        if connection not in duplicates:
            dot += connection
            duplicates.append(connection)



    '''
    for ms in multi_subjects:
        mss = []
        for s in services:
            for subject in s['subjects']:
                if subject.split(':')[0] in ms:
                    mss.append(subject.split(':')[1] + '_' + subject.split(':')[0])
        dot+= group(mss, '', 'subject_')
    '''


    dot += '}\n'


    with open('async_reg.dot', 'w') as f:
        for l in dot.splitlines():
            print(l, file = f)

    return dot


def gen_dot_async_invokations(clients, services, tples, async_messages, async_actions):

    dot = ''
    dot += 'digraph {\n'
    dot += 'bgcolor=lightcyan\n'
    dot += 'rankdir=LR\n'
    dot += 'nodesep=\"0.05\"\n'
    dot += 'ranksep=\"2.5\"\n'

    dot += 'fontname="Arial"; fontsize=16; fontcolor=grey\n'
    dot += 'label="Utopia Async Invokations"\n'
    dot += 'labelloc=top\n'
    dot += 'labeljust="l"\n'
    dot += 'edge [color=black arrowsize=0.5 penwidth=0.1]\n'


    actions = []
    client = ''
    for d in debug:
        if d.split('|')[0] in ['OPEN_CONNECTION']:
            client = d.split('|')[1]
        if d.split('|')[0] == 'RUN_EXTERNAL_EXECUTABLE':
            ds = d.split('|')
            fn = '?'
            for a in async_actions:
                if a.split('|')[0] == ds[3]:
                    fn = a.split('|')[2].split('/')[-1]
                    break;

            actions.append(ds[1] + '|' + ds[2] + '|' + fn + '|' + client)


    notifications = []
    client = ''
    for d in debug:
        if d.split('|')[0] in ['OPEN_CONNECTION']:
            client = d.split('|')[1]
        if d.split('|')[0] == 'SEND_NOTIFICATION':
            ds = d.split('|')
            nt = '?'
            for a in async_messages:
                if a.split('|')[0] == ds[3]:
                    nt = a.split('|')[2]
                    break;

            notifications.append(ds[1] + '|' + ds[2] + '|' + nt + '|' + client)





    # notifications

    dot += 'subgraph cluster' + hash('notifications') + ' {\n'

    dot += 'margin=3;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('notifications', 1)
    dot += 'color=\"%s\";\n' %getcolor('notifications', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('notifications', 3)
    dot += 'fontsize=10;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=\"0.1\" penwidth=0.1];\n'
    dot += 'label=\"' + 'notifications' + '\\l' + '\";\n'
    dot += 'style=\"filled, rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')

    for a in notifications:

        notification = a.split('|')[0] + ':' + a.split('|')[1]

        label=notification+'\\l'
        fontsize=8
        style='filled'
        width=0
        shape='box'
        fillcolor=getcolor('notifications', 2)
        color=getcolor('notifications', 4)
        fontcolor=getcontrastcolor(getcolor('notifications', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('notification_' + notification), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'



    subclients = []

    for a in notifications:
        if a.split('|')[3] not in subclients:
            subclients.append(a.split('|')[3])
    for a in actions:
        if a.split('|')[3] not in subclients:
            subclients.append(a.split('|')[3])


    # clients

    m = {}
    for c in client_mappings.splitlines():
        if c:
            #print('[' + c + ']')
            m[c.split(':')[0]] = c.split(':')[1]


    dot += 'subgraph cluster' + hash('clients') + ' {\n'

    dot += 'margin=6;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('clients', 1)
    dot += 'color=\"%s\";\n' %getcolor('clients', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('clients', 3)
    dot += 'fontsize=14;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=\"0.1\" penwidth=0.1];\n'
    dot += 'label=\"' + 'clients' + '\\l' + '\";\n'
    dot += 'style=\"filled, rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')

    for client in subclients:

        label=m[client] + '\n' + '\'' + client + '\''
        fontsize=12
        style='filled,rounded'
        width=0
        shape='box'
        fillcolor=getcolor('clients', 2)
        color=getcolor('clients', 4)
        fontcolor=getcontrastcolor(getcolor('clients', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('client_' + client), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'





    # actions

    dot += 'subgraph cluster' + hash('actions') + ' {\n'

    dot += 'margin=3;\n'
    dot += 'penwidth=1.0;\n'
    dot += 'fillcolor=\"%s\";\n' %getcolor('actions', 1)
    dot += 'color=\"%s\";\n' %getcolor('actions', 3)
    dot += 'fontcolor=\"%s\";\n' %getcolor('actions', 3)
    dot += 'fontsize=12;\n'
    dot += 'node[fontname=\"Arial\" height=0 margin=0 penwidth=0.1];\n'
    dot += 'label=\"' + 'actions' + '\\l' + '\";\n'
    dot += 'style=\"filled,rounded\";\n'

    dot += '%s [label=\"\" shape=plaintext style=invisible]\n' %hash('clients')

    for a in actions:

        action = a.split('|')[0] + ':' + a.split('|')[1] + ':' + a.split('|')[2]

        label=action+'\\l'
        fontsize=10
        style='filled'
        width=4
        shape='box'
        fillcolor=getcolor('actions', 2)
        color=getcolor('actions', 4)
        fontcolor=getcontrastcolor(getcolor('actions', 2))
        tooltip=''
        url=''

        dot+= "%s [label=\"%s\" fontsize=%d style=\"%s\" width=\"%s\" shape=\"%s\" fillcolor=\"%s\" color=\"%s\" fontcolor=\"%s\" tooltip=\"%s\" URL=\"%s\"]\n" \
        % (hash('action_' + action), label, fontsize, style, width, shape, fillcolor, color, fontcolor, tooltip, url)

    dot += '}\n'



    duplicates = []

    for a in notifications:
        connection = '%s -> %s[arrowhead=none];\n' %(hash('client_' + a.split('|')[3]), hash('notification_' + a.split('|')[0] + ':' + a.split('|')[1]))
        if connection not in duplicates:
            dot += connection
            duplicates.append(connection)


    for a in actions:
        connection = '%s -> %s[arrowhead=none];\n' %(hash('action_' + a.split('|')[0] + ':' + a.split('|')[1] + ':' + a.split('|')[2]), hash('client_' + a.split('|')[3]))
        if connection not in duplicates:
            dot += connection
            duplicates.append(connection)



    dot += '}\n'


    with open('async_inv.dot', 'w') as f:
        for l in dot.splitlines():
            print(l, file = f)

    return dot




def gen_html(clients, services, tples, async_messages, debug):

    a_head = """

    <!DOCTYPE html>
    <html>
    <head>
    <title>Utopia Service Map</title>
    </head>
    <style>

    #maincontent, html, body {
        height: 99%;
        background: #E0FFFF
    }
    #left {
        float: left;
        width: 70%;
        height: 100%;
        overflow: auto;
    }
    #right {
        float: left;
        padding-left: 1%;
        width: 29%;
        height: 100%;
        overflow: auto;
    }


    .syseventd {
        font-family: Arial;
        font-size: 20px;
        color: grey;
    }

    .collapsible {
        background-color: #777;
        color: white;
        cursor: pointer;
        padding: 2px;
        width: 100%;
        border: 1px solid #E0FFFF;
        text-align: left;
        outline: hidden;
        font-size: 12px;
    }

    .active, .collapsible:hover {
        background-color: #555;
    }

    .content {
        padding: 0;
        width: 100%;
        display: none;
        overflow: visible;
        background-color: #E0FFFF;
    }

    p {
        padding-bottom: 1000px;
      }

    </style>

    <body>
    """

    a_tail = """

    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
        });
    }
    </script>

    </body>
    </html>
    """

    svg_service_map = subprocess.Popen("dot -Kdot -Tsvg", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=None, shell=True).communicate(input = gen_dot_service_map(clients, services, tples, async_actions, async_messages).encode())[0].decode(encoding='UTF-8')
    svg_async_registrations = subprocess.Popen("dot -Kdot -Tsvg", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=None, shell=True).communicate(input = gen_dot_async_registrations(clients, services, tples, async_messages).encode())[0].decode(encoding='UTF-8')
    svg_async_invokations = subprocess.Popen("dot -Kdot -Tsvg", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=None, shell=True).communicate(input = gen_dot_async_invokations(clients, services, tples, async_messages, async_actions).encode())[0].decode(encoding='UTF-8')

    with open(sys.argv[1] + '.map.html', 'w') as f:


        print(a_head,file = f)

        print('<div id="maincontent">', file = f)

        ### LEFT PANEL
        print('<div id="left">', file = f)

        print(svg_service_map, file = f)
        print(svg_async_registrations, file = f)
        print(svg_async_invokations, file = f)
        print('</div>', file = f)


        ### RIGHT PANEL
        print('<div id="right">', file =f)
        print('<div class="syseventd">', file =f)
        print('Sysevent Daemon</br></br>', file = f)
        print('</div>', file =f)


        ### README

        print('<button type="button" class="collapsible">README..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        for l in readme.splitlines():
            print('%s</br>' %(l), file = f)

        print('</br>', file = f)
        print('</div>', file = f)


        ### DEBUG

        print('<button type="button" class="collapsible">DEBUG..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        for d in debug:
            print('%s</br>' %(d), file = f)

        print('</br>', file = f)
        print('</div>', file = f)


        ### SET
        print('<button type="button" class="collapsible">SET..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        client = ''
        current_client = ''
        for d in debug:
            if d.split('|')[0] in ['OPEN_CONNECTION']:
                client = d.split('|')[1]
            if d.split('|')[0] == 'SET':
                if current_client != client:
                    print('<span style=\"color:red;font-weight:bold\">%s</span></br>' %(client + ':'), file = f)
                    current_client = client
                ds = d.split('|')
                if not 'async_id' in ds[1]:
                    print('%s &#8592; \'%s\'</br>' %(ds[1],ds[2]), file = f)

        print('</br>', file = f)
        print('</div>', file = f)


        ### GET
        print('<button type="button" class="collapsible">GET..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        client = ''
        current_client = ''
        for d in debug:
            if d.split('|')[0] in ['OPEN_CONNECTION']:
                client = d.split('|')[1]
            if d.split('|')[0] == 'GET_REPLY':
                if current_client != client:
                    print('<span style=\"color:red;font-weight:bold\">%s</span></br>' %(client + ':'), file = f)
                    current_client = client
                ds = d.split('|')
                if not 'async_id' in ds[1]:
                    print('%s &#8594; \'%s\'</br>' %(ds[1],ds[2]), file = f)
                    #print('<a href=\"#link%d\">%s</a>%s</br>' %(0,0,'hello'), file = f)

        print('</br>', file = f)
        print('</div>', file = f)


        ### RUN_EXTERNAL_EXECUTABLE

        print('<button type="button" class="collapsible">RUN_EXTERNAL_EXECUTABLE..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        client = ''
        current_client = ''
        runs = []
        for d in debug:
            if d.split('|')[0] in ['OPEN_CONNECTION']:
                client = d.split('|')[1]
                runs = []
            elif d.split('|')[0] == 'RUN_EXTERNAL_EXECUTABLE':
                if current_client != client:
                    print('<span style=\"color:red;font-weight:bold\">%s</span></br>' %(client + ':'), file = f)
                    current_client = client
                ds = d.split('|')

                fn = '?'
                for a in async_actions:
                    if a.split('|')[0] == ds[3]:
                        fn = a.split('|')[2].split('/')[-1]
                        break;

                color = 'black'
                if ds[1] + ':' + ds[2] + ':' + fn not in runs:
                    runs.append(ds[1] + ':' + ds[2] + ':' + fn)
                else:
                    #color = 'lightgrey'
                    continue

                print('<span style=\"color:%s\">&nbsp&nbsp&nbsp %s &#8592; \'%s\' &#128498; ./%s</span></br>' %(color, ds[1], ds[2], fn), file = f)

        print('</br>', file = f)
        print('</div>', file = f)


        ### SEND_NOTIFICATION

        print('<button type="button" class="collapsible">SEND_NOTIFICATION...</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)


        client = ''
        current_client = ''
        runs = []
        for d in debug:
            if d.split('|')[0] in ['OPEN_CONNECTION']:
                client = d.split('|')[1]
                runs = []
            elif d.split('|')[0] == 'SEND_NOTIFICATION':
                if current_client != client:
                    print('<span style=\"color:red;font-weight:bold\">%s</span></br>' %(client +':'), file = f)
                    current_client = client
                ds = d.split('|')

                nt = '?'
                for a in async_messages:
                    if a.split('|')[0] == ds[3]:
                        nt = a.split('|')[2]
                        break;

                color = 'black'
                if ds[1] + ':' + ds[2] + ':' + fn not in runs:
                    runs.append(ds[1] + ':' + ds[2] + ':' + fn)
                else:
                    #color = 'lightgrey'
                    continue

                print('<span style=\"color:%s\">&nbsp&nbsp&nbsp %s &#8592; \'%s\' &#128498; ./%s</span></br>' %(color, ds[1], ds[2], nt), file = f)

        print('</br>', file = f)
        print('</div>', file = f)




        ### CLIENTS

        print('<button type="button" class="collapsible">CLIENTS..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        m = {}
        for c in client_mappings.splitlines():
            if c:
                m[c.split(':')[0]] = c.split(':')[1]

        for client in clients:
            print('%s \"%s\"</br>' %(m[client], client), file = f)

        print('</br>', file = f)
        print('</div>', file = f)



        ### TUPLES

        print('<button type="button" class="collapsible">TUPLES..</button>', file = f)
        print('<div class="content">', file = f)

        print('</br>', file = f)

        for t in sorted(tples, key=lambda x: x['subject'].lower()):

            if not '_async_id_' in t['subject']:
                ts = t['subject']

                vs = ''
                os = ''
                if t['values']:
                    vs =','.join('\'' + x.split(':')[0] + '\'' + ':' + x.split(':')[1] for x in t['values'])
                    vs = '(' + vs + ')'
                if t['options']:
                    os = ','.join(t['options'])
                    os = '[' + os + ']'

                mark = ''
                if t['async_action'] and not t['async_message']:
                    mark = '*'
                elif t['async_message'] and not t['async_action']:
                    mark = '+'
                elif t['async_action'] and t['async_message']:
                    mark = '*+'

                color = 'black'
                if not t['async_action'] and not t['async_message'] and not t['gets']:
                    color = 'grey'
                print('<span style=\"color:%s\">%s%s%s%s</span></br>' %(color, mark, ts, vs, os), file = f)





        print('</br>', file = f)
        print('</div>', file = f)




        print('</div>', file = f)
        print('</div>', file = f)

        print(a_tail, file = f)

    print(sys.argv[1] + '.map.html')


def checklines(lines, linenr, items, errors):

    #print('[' + lines[linenr] + ']')
    j = 1
    for item in items:
        if not lines[linenr + j].startswith('| ' + item):
            #print('parse_error:', linenr, '[' + lines[linenr + j] + ']', item)
            errors.append(str(linenr + 1) + ':' + lines[linenr] + ':' + lines[linenr + j] + '!=' + item)
            return True
        j+= 1

    if lines[linenr] != '|-------- SE_MSG_SET_ASYNC_ACTION -------|':

        if lines[linenr + j] != '|----------------------------------------|':
            errors.append(str(linenr + 1) + ':' + lines[linenr] + ':' + lines[linenr + j + 1] + '!=' + 'ending line')
            return True

    return False


def parse_full(f):
    debug = []
    lines = []
    with open(f, 'r') as fp:
        lines = fp.read().splitlines()

    #sys.stderr.write("parsing \"%s\" ...\n" %sys.argv[1])

    errors = []

    linenr = 0
    while linenr < len(lines):

        #print(linenr)

        if lines[linenr] == '|------- SE_MSG_OPEN_CONNECTION ---------|':
        #|------- SE_MSG_OPEN_CONNECTION ---------|
        #| version       : 1
        #| id_bytes      : 24
        #| id            : system_default_set
        #|----------------------------------------|

            if checklines(lines, linenr, ['version', 'id_bytes', 'id'], errors):
                linenr+= 1
                continue

            id = lines[linenr+3].split(': ')[1].strip()
            debug.append('%s|%s|' %('OPEN_CONNECTION', id))
            linenr+=5

        elif lines[linenr] == '|------ SE_MSG_OPEN_CONNECTION_REPLY ----|':
        #|------ SE_MSG_OPEN_CONNECTION_REPLY ----|
        #| status        : 0x0
        #| token_id      : 1
        #|----------------------------------------|
            if checklines(lines, linenr, ['status', 'token_id'], errors):
                linenr+= 1
                continue

            debug.append('%s|' %('OPEN_CONNECTION_REPLY'))
            linenr+=4

        elif lines[linenr] == '|---------- SE_MSG_NEW_CLIENT -----------|':
        #|---------- SE_MSG_NEW_CLIENT -----------|
        #| token_id      : 1
        #|----------------------------------------|
            if checklines(lines, linenr, ['token_id'], errors):
                linenr+= 1
                continue

            debug.append('%s|' %('NEW_CLIENT'))
            linenr+=3

        elif lines[linenr] == '|------- SE_MSG_CLOSE_CONNECTION --------|':
        #|------- SE_MSG_CLOSE_CONNECTION --------|
        #|----------------------------------------|
            if debug.append('%s|' %('CLOSE_CONNECTION')):
                linenr+= 1
                continue

            linenr+=2

        elif lines[linenr] == '|------------- SE_MSG_GET ---------------|':
        #|------------- SE_MSG_GET ---------------|
        #| subject_bytes : 16
        #| subject       : wan_ifname
        #|----------------------------------------|
            if checklines(lines, linenr, ['subject_bytes', 'subject'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+2].split(': ')[1].strip()
            debug.append('%s|%s|' %('GET', subject))
            linenr+=4

        elif lines[linenr] == '|------------ SE_MSG_GET_REPLY ----------|':
        #|------------ SE_MSG_GET_REPLY ----------|
        #| status        : 0x0
        #| subject_bytes : 16
        #| value_bytes   : 8
        #| subject       : model_name
        #| value         : 
        #|----------------------------------------|
            if checklines(lines, linenr, ['status', 'subject_bytes', 'value_bytes', 'subject', 'value'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+4].split(': ')[1].strip()
            value = lines[linenr+5].split(': ')[1].strip()
            debug.append('%s|%s|%s|' %('GET_REPLY', subject, value))
            linenr+=7

        elif lines[linenr] == '|----------- SE_MSG_ITERATE_GET ---------|':
        #|----------- SE_MSG_ITERATE_GET ---------|
        #| iterator      : ffffffff
        #| subject_bytes : 20
        #| subject       : NatFirewallRule
        #|----------------------------------------|
            if checklines(lines, linenr, ['iterator', 'subject_bytes', 'subject'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+3].split(': ')[1].strip()
            debug.append('%s|%s|' %('ITERATE_GET', subject))
            linenr+=5

        elif lines[linenr] == '|-------- SE_MSG_ITERATE_GET_REPLY ------|':
        #|-------- SE_MSG_ITERATE_GET_REPLY ------|
        #| status        : 0x0
        #| iterator      : ffffffff
        #| subject_bytes : 8
        #| value_bytes   : 8
        #| subject       : 1
        #| value         : 
        #|----------------------------------------|
            if checklines(lines, linenr, ['status', 'iterator', 'subject_bytes', 'value_bytes', 'subject', 'value'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+5].split(': ')[1].strip()
            value = lines[linenr+6].split(': ')[1].strip()
            debug.append('%s|%s|%s|' %('ITERATE_GET_REPLY', subject, value))
            linenr+=8

        elif lines[linenr] == '|--------- SE_MSG_NOTIFICATION ----------|':
        #|--------- SE_MSG_NOTIFICATION ----------|
        #| source        : -785457145
        #| tid           : -704643072
        #| async_id      : 0x27000000 0x2000000
        #| subject_bytes : 16
        #| subject       : pnm-status
        #| value_bytes   : 8
        #| value         : up
        #|----------------------------------------|
            if checklines(lines, linenr, ['source', 'tid', 'async_id', 'subject_bytes', 'subject', 'value_bytes', 'value'], errors):
                linenr+= 1
                continue

            async_id = lines[linenr+3].split(': ')[1].strip()
            subject = lines[linenr+5].split(': ')[1].strip()
            value = lines[linenr+7].split(': ')[1].strip()
            debug.append('%s|%s|%s|%s|' %('NOTIFICATION', subject, value, async_id))
            linenr+=9

        elif lines[linenr] == '|---------- SE_MSG_REMOVE_ASYNC ---------|':
        #|---------- SE_MSG_REMOVE_ASYNC ---------|
        #| async_id      : 0x24000000 0x1000000
        #|----------------------------------------|
            if checklines(lines, linenr, ['async_id'], errors):
                linenr+= 1
                continue

            async_id = lines[linenr+1].split(': ')[1].strip()
            debug.append('%s|%s|' %('REMOVE_ASYNC', async_id))
            linenr+=3

        elif lines[linenr] == '|---- SE_MSG_RUN_EXTERNAL_EXECUTABLE ----|':
        #|---- SE_MSG_RUN_EXTERNAL_EXECUTABLE ----|
        #| token_id      : e
        #| async_id      : 0x27000000 0x1000000
        #| flags         : 0x0
        #| subject_bytes : 16
        #| subject       : pnm-status
        #| value_bytes   : 8
        #| value         : up
        #|----------------------------------------|
            if checklines(lines, linenr, ['token_id','async_id','flags','subject_bytes','subject','value_bytes', 'value'], errors):
                linenr+= 1
                continue

            async_id = lines[linenr+2].split(': ')[1].strip()
            flags = lines[linenr+3].split(': ')[1].strip()
            subject = lines[linenr+5].split(': ')[1].strip()
            value = lines[linenr+7].split(': ')[1].strip()
            debug.append('%s|%s|%s|%s|%s|' %('RUN_EXTERNAL_EXECUTABLE', subject, value, async_id, flags))
            linenr+=9

        elif lines[linenr] == '|------- SE_MSG_SEND_NOTIFICATION -------|':
        #|------- SE_MSG_SEND_NOTIFICATION -------|
        #| source        : -785457145
        #| tid           : -704643072
        #| token_id      : 36
        #| async_id      : 0x27000000 0x2000000
        #| flags         : 0x0
        #| subject_bytes : 16
        #| subject       : pnm-status
        #| value_bytes   : 8
        #| value         : up
        #|----------------------------------------|
            if checklines(lines, linenr, ['source', 'tid', 'token_id', 'async_id','flags','subject_bytes','subject','value_bytes', 'value'], errors):
                linenr+= 1
                continue

            async_id = lines[linenr+4].split(': ')[1].strip()
            flags = lines[linenr+5].split(': ')[1].strip()
            subject = lines[linenr+7].split(': ')[1].strip()
            value = lines[linenr+9].split(': ')[1].strip()
            debug.append('%s|%s|%s|%s|%s|' %('SEND_NOTIFICATION', subject, value, async_id, flags))
            linenr+=11

        elif lines[linenr] == '|-------------- SE_MSG_SET --------------|':
        #|-------------- SE_MSG_SET --------------|
        #| source        : 0
        #| tid           : 0
        #| subject_bytes : 16
        #| value_bytes   : 16
        #| subject       : wan_ifname
        #| value         : erouter0
        #|----------------------------------------|
            if checklines(lines, linenr, ['source', 'tid', 'subject_bytes','value_bytes','subject', 'value'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+5].split(': ')[1].strip()
            value = lines[linenr+6].split(': ')[1].strip()
            debug.append('%s|%s|%s|' %('SET', subject, value))
            linenr+=8

        elif lines[linenr] == '|-------- SE_MSG_SET_ASYNC_ACTION -------|':
        #|-------- SE_MSG_SET_ASYNC_ACTION -------|
        #| flags         : 0x0
        #| num_params    : 1
        #| subject_bytes : 20
        #| subject       : bridge-start
        #| function_bytes: 56
        #| function      : /etc/utopia/service.d/service_bridge_brcm93390.sh
        #| param_bytes   : 20
        #| param         : bridge-start
        #|----------------------------------------|
            if checklines(lines, linenr, ['flags', 'num_params', 'subject_bytes', 'subject', 'function_bytes', 'function'], errors):
                linenr+= 1
                continue

            flags = lines[linenr+1].split(': ')[1].strip()
            num_params = lines[linenr+2].split(': ')[1].strip()
            subject = lines[linenr+4].split(': ')[1].strip()
            function = lines[linenr+6].split(': ')[1].strip()
            debug.append('%s|%s|%s|%s|' %('SET_ASYNC_ACTION', subject, function, flags))

            linenr+=10 if num_params == '1' else 8

        elif lines[linenr] == '|-------- SE_MSG_SET_ASYNC_MESSAGE ------|':
        #|-------- SE_MSG_SET_ASYNC_MESSAGE ------|
        #| subject_bytes : 20
        #| subject       : erouter_mode
        #| flags         : 0x0
        #|----------------------------------------|
            if checklines(lines, linenr, ['subject_bytes','subject','flags'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+2].split(': ')[1].strip()
            flags = lines[linenr+3].split(': ')[1].strip()
            debug.append('%s|%s|%s|' %('SET_ASYNC_MESSAGE', subject, flags))
            linenr+=5

        elif lines[linenr] == '|------- SE_MSG_SET_ASYNC_REPLY ---------|':
        #|------- SE_MSG_SET_ASYNC_REPLY ---------|
        #| status        : 0x0
        #| async_id      : 0x3000000 0x1000000
        #|----------------------------------------|
            if checklines(lines, linenr, ['status', 'async_id'], errors):
                linenr+= 1
                continue

            async_id = lines[linenr+2].split(': ')[1].strip()
            debug.append('%s|%s|' %('SET_ASYNC_REPLY', async_id))
            linenr+=4

        elif lines[linenr] == '|---------- SE_MSG_SET_OPTIONS ----------|':
        #|---------- SE_MSG_SET_OPTIONS ----------|
        #| subject_bytes : 16
        #| subject       : model_name
        #| flags         : 0x4
        #|----------------------------------------|
            if checklines(lines, linenr, ['subject_bytes','subject','flags'], errors):
                linenr+= 1
                continue

            subject = lines[linenr+2].split(': ')[1].strip()
            flags = lines[linenr+3].split(': ')[1].strip()
            debug.append('%s|%s|%s|' %('SET_OPTIONS', subject, flags))
            linenr+=5

        elif lines[linenr] == '|------ SE_MSG_SET_OPTIONS_REPLY --------|':
        #|------ SE_MSG_SET_OPTIONS_REPLY --------|
        #| status        : 0x0
        #|----------------------------------------|
            if checklines(lines, linenr, ['status'], errors):
                linenr+= 1
                continue

            debug.append('%s|' %('SET_OPTIONS_REPLY'))
            linenr+=3

        #|----------- SE_MSG_SET_REPLY -----------|
        #| status        : 0x0
        #|----------------------------------------|
        elif lines[linenr] == '|----------- SE_MSG_SET_REPLY -----------|':
            if checklines(lines, linenr, ['status'], errors):
                linenr+= 1
                continue

            debug.append('%s|' %('SET_REPLY'))
            linenr+=3

        else:
            print('skip line')
            linenr+= 1


    for error in errors:
        print(error)

    #exit()

    for d in debug:

        #print (d)

        type = d.split('|')[0]

        if type == 'OPEN_CONNECTION':
            pass
        elif type == 'CLOSE_CONNECTION':
            pass
        elif type == 'GET':
            pass
        elif type == 'GET_REPLY':
            pass
        elif type == 'ITERATE_GET':
            pass
        elif type == 'ITERATE_GET_REPLY':
            pass
        elif type == 'NEW_CLIENT':
            pass
        elif type == 'NOTIFICATION':
            pass
        elif type == 'OPEN_CONNECTION_REPLY':
            pass
        elif type == 'REMOVE_ASYNC':
            pass
        elif type == 'RUN_EXTERNAL_EXECUTABLE':
            pass
        elif type == 'SEND_NOTIFICATION':
            pass
        elif type == 'SET':
            pass
        elif type == 'SET_ASYNC_ACTION':
            pass
        elif type == 'SET_ASYNC_MESSAGE':
            pass
        elif type == 'SET_ASYNC_REPLY':
            pass
        elif type == 'SET_OPTIONS':
            pass
        elif type == 'SET_OPTIONS_REPLY':
            pass
        elif type == 'SET_REPLY':
            pass
        else:
            print('parse error')
            exit()

    return debug


def parse_minimal(f):

    with open(f, 'r') as fp:
        lines = fp.read().splitlines()

    #sys.stderr.write("parsing \"%s\" ...\n" %sys.argv[1])


    # remove the timestamps
    for i in range(len(lines)):
        parts = lines[i].split('|')
        lines[i] = '|' + '|'.join(parts[1:])


    debug = []

    for line in lines:

        #print(line)

        items = line.split('|')[1:]
        #print(items)

        if line.startswith('|sysevent_'):
            pass

        elif line.startswith('|SE_MSG_OPEN_CONNECTION|'):
            #|SE_MSG_OPEN_CONNECTION|system_default_set|
            debug.append('%s|%s|' %('OPEN_CONNECTION', items[1].strip()))

        elif line.startswith('|SE_MSG_OPEN_CONNECTION_REPLY|'):
            #|SE_MSG_OPEN_CONNECTION_REPLY|1|
            debug.append('%s|' %('OPEN_CONNECTION_REPLY'))

        elif line.startswith('|SE_MSG_NEW_CLIENT|'):
            #|SE_MSG_NEW_CLIENT|1|
            debug.append('%s|' %('NEW_CLIENT'))

        elif line.startswith('|SE_MSG_CLOSE_CONNECTION|'):
            #|SE_MSG_CLOSE_CONNECTION|
            debug.append('%s|' %('CLOSE_CONNECTION'))

        elif line.startswith('|SE_MSG_GET|'):
            #|SE_MSG_GET|FW_LOG_FILE_PATH_V2|
            debug.append('%s|%s|' %('GET', items[1].strip()))

        elif line.startswith('|SE_MSG_GET_REPLY|'):
            #|SE_MSG_GET_REPLY|FW_LOG_FILE_PATH_V2||
            debug.append('%s|%s|%s|' %('GET_REPLY', items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_ITERATE_GET|'):
            #|SE_MSG_ITERATE_GET|ffffffff|NatFirewallRule|
            debug.append('%s|%s|' %('ITERATE_GET', items[1].strip()))

        elif line.startswith('|SE_MSG_ITERATE_GET_REPLY'):
            #|-------- SE_MSG_ITERATE_GET_REPLY ------|
            debug.append('%s|%s|%s|' %('ITERATE_GET_REPLY', items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_NOTIFICATION|'):
            #|SE_MSG_NOTIFICATION|0x28 0x2|bring-lan|up|
            debug.append('%s|%s|%s|%s|' %('NOTIFICATION', items[2].strip(), items[3].strip(),items[1].strip()))

        elif line.startswith('|SE_MSG_REMOVE_ASYNC|'):
            #|SE_MSG_REMOVE_ASYNC|0x24 0x1|
            debug.append('%s|%s|' %('REMOVE_ASYNC', items[1].strip()))

        elif line.startswith('|SE_MSG_RUN_EXTERNAL_EXECUTABLE|'):
            #|SE_MSG_RUN_EXTERNAL_EXECUTABLE|0x28 0x1|0x0|bring-lan|up|
            debug.append('%s|%s|%s|%s|%s|' %('RUN_EXTERNAL_EXECUTABLE', items[3].strip(), items[4].strip(), items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_SEND_NOTIFICATION|'):
            #|SE_MSG_SEND_NOTIFICATION|0x3e 0x1|0x0|lan-status|started|
            debug.append('%s|%s|%s|%s|%s|' %('SEND_NOTIFICATION', items[3].strip(), items[4].strip(), items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_SET|'):
            #|SE_MSG_SET|ipv4_6-ifname|brlan7|
            debug.append('%s|%s|%s|' %('SET', items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_SET_ASYNC_ACTION|'):
            #|SE_MSG_SET_ASYNC_ACTION|0x0|1|bridge-start|/etc/utopia/service.d/service_bridge.sh|
            debug.append('%s|%s|%s|%s|' %('SET_ASYNC_ACTION', items[3].strip(), items[4].strip(),items[1].strip()))

        elif line.startswith('|SE_MSG_SET_ASYNC_MESSAGE|'):
            #|SE_MSG_SET_ASYNC_MESSAGE|0x0|erouter_mode|
            debug.append('%s|%s|%s|' %('SET_ASYNC_MESSAGE', items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_SET_ASYNC_REPLY|'):
            #|SE_MSG_SET_ASYNC_REPLY|0x8c 0x1|
            debug.append('%s|%s|' %('SET_ASYNC_REPLY', items[1].strip()))

        elif line.startswith('|SE_MSG_SET_OPTIONS|'):
            #|SE_MSG_SET_OPTIONS|cosa-restart|0x2|
            debug.append('%s|%s|%s|' %('SET_OPTIONS', items[1].strip(), items[2].strip()))

        elif line.startswith('|SE_MSG_SET_OPTIONS_REPLY|'):
            #|SE_MSG_SET_OPTIONS_REPLY|
            debug.append('%s|' %('SET_OPTIONS_REPLY'))

        elif line.startswith('|SE_MSG_SET_REPLY|'):
            #|SE_MSG_SET_REPLY|
            debug.append('%s|' %('SET_REPLY'))

        else:
            print('@IGNORE (LINE#%s):'%(lines.index(line) + 1) , line)
            pass
            #exit()


    for d in debug:

        #print (d)

        type = d.split('|')[0]

        if type == 'OPEN_CONNECTION':
            pass
        elif type == 'CLOSE_CONNECTION':
            pass
        elif type == 'GET':
            pass
        elif type == 'GET_REPLY':
            pass
        elif type == 'ITERATE_GET':
            pass
        elif type == 'ITERATE_GET_REPLY':
            pass
        elif type == 'NEW_CLIENT':
            pass
        elif type == 'NOTIFICATION':
            pass
        elif type == 'OPEN_CONNECTION_REPLY':
            pass
        elif type == 'REMOVE_ASYNC':
            pass
        elif type == 'RUN_EXTERNAL_EXECUTABLE':
            pass
        elif type == 'SEND_NOTIFICATION':
            pass
        elif type == 'SET':
            pass
        elif type == 'SET_ASYNC_ACTION':
            pass
        elif type == 'SET_ASYNC_MESSAGE':
            pass
        elif type == 'SET_ASYNC_REPLY':
            pass
        elif type == 'SET_OPTIONS':
            pass
        elif type == 'SET_OPTIONS_REPLY':
            pass
        elif type == 'SET_REPLY':
            pass
        else:
            print('parse error')
            exit()

    return debug


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("usage: %s syseventd.out" %(sys.argv[0]))
        exit()

    #debug =    parse_full(sys.argv[1])

    debug = parse_minimal(sys.argv[1])

    ############################################
    #
    # obtain list of clients from 'OPEN_CONNECTION'
    #
    clients = []

    for d in debug:
        if d.split('|')[0] in ['OPEN_CONNECTION']:
            if d.split('|')[1] not in clients:
                clients.append(d.split('|')[1])
    #for c in clients:
    #   print(c)
    #exit()

    ############################################
    #
    # check whether an SET_ASYNC_MESSAGE was not immediately followed  by an SET_ASYNC_REPLY
    # in which case we need the input file to be manually edited/corrected
    #
    for i in range(len(debug)):
        d = debug[i]
        if d.split('|')[0] in ['SET_ASYNC_MESSAGE']:
            if i < len(debug):
                if debug[i + 1].split('|')[0] != 'SET_ASYNC_REPLY':
                    print('Warning: No SET_ASYNC_REPLY after SET_ASYNC_MESSAGE - around linenr:' + str(i), d)
                    #exit()


    ############################################
    #
    # obtain list of async_actions from SET_ASYNC_ACTION
    # for each ASYNC_ACTION record the async_id, the subject, the function, and the client
    #
    # SET_ASYNC_ACTION will specify the subject and the function
    # SET_ASYNC_REPLY that immediately follows will specify the async id
    # SET with an 'async_id_' : |SE_MSG_SET|xsm_multinet_async_id_multinet-stop|multinet-stop 0x9f000000 0x1000000| will also specify the async id
    #
    # a SET with an 'async_id_' with a matching subject is used to obtain the aysnc id if this does not occur then SET_ASYNC_REPLY is searched for
    # if a subject + function already exists then 
    # an async_action can be removed usually to set a new function or to set a new option
    #
    # record all async id removals and remove them from the async_actions

    async_actions = []
    client = ''
    for i in range(len(debug)):
        d = debug[i]

        ############################################
        if d.split('|')[0] in ['OPEN_CONNECTION']:
            client = d.split('|')[1]

        elif d.split('|')[0] in ['SET_ASYNC_ACTION']:

            s = d.split('|')[1]
            f = d.split('|')[2]

            found = False
            for d2 in debug[i:]:
                if d2.split('|')[0] in ['SET'] and '_async_id_' in d2.split('|')[1] and d2.split('|')[2].startswith(s):
                    async_actions.append(d2.split('|')[2].split(s)[1][1:] + '|' + s + '|' + f + '|' + client)
                    found = True
                    break

            if not found:
                #print('\'async set id\' not found, checking \'async_reply\'', d)
                found = False
                for d3 in debug[i:]:
                    if d3.split('|')[0] in ['SET_ASYNC_REPLY']:
                        found = True
                        async_actions.append(d3.split('|')[1] + '|' + s + '|' + f + '|' + client)
                        break
                if not found:
                    print('\'async reply\' not found\'', d)
                    exit()
                else:
                    #print('\'async reply\' found\'', d)
                    pass

    #for a in async_actions:
    #   print('aa=', a)
    #exit()

    async_removed = []
    for d in debug:
        if d.split('|')[0] in ['REMOVE_ASYNC']:
            async_removed.append(d.split('|')[1])
    #for ar in async_removed:
    #   print(ar)

    for aa in async_actions:
        for ar in async_removed:
            if aa.split('|')[0] == ar:
                #print('removing:', ar)
                async_actions.remove(aa)

    #for a in async_actions:
    #   print('aa=', a)
    #exit()

    ############################################
    # obtain list of async_messages from SET_ASYNC_MESSAGE
    # for each ASYNC_MESSAGE record the subject,
    # and check the next line for ASYNC_REPLAY and pick up the async id
    #

    async_messages = []
    client = ''
    for i in range(len(debug)):
        d = debug[i]
        ############################################
        if d.split('|')[0] in ['OPEN_CONNECTION']:
            client = d.split('|')[1]

        elif d.split('|')[0] in ['SET_ASYNC_MESSAGE']:
            s = d.split('|')[2]

            if debug[i + 1].split('|')[0] in ['SET_ASYNC_REPLY']:
                async_messages.append(debug[i + 1].split('|')[1] + '|' + s + '|' + client)
            else:
                #print('Warning: No ASYNC_MESSAGE + ASYNC_REPLY')
                break;

    #for a in async_messages:
    #   print('am=', a)
    #exit()

    ############################################
    # build services list
    #
    services = []
    for d in debug:

        ############################################
        if d.split('|')[0] in ['SET']:

            s = d.split('|')[1]
            v = d.split('|')[2]
            if s.startswith('xsm_'):

                #|SE_MSG_SET|xsm_ipv6_async_id_ipv6-start|ipv6-start 0x15000000 0x1000000|
                #|SE_MSG_SET|xsm_ipv6_async_id_ipv6-stop|ipv6-stop 0x16000000 0x1000000|
                #|SE_MSG_SET|xsm_ipv6_async_id_ipv6-restart|ipv6-restart 0x17000000 0x1000000|
                #|SE_MSG_SET|xsm_ipv6_async_id_1|ipv6_prefix 0x18000000 0x1000000|
                #|SE_MSG_SET|xsm_ipv6_async_id_2|multinet-instances 0x19000000 0x1000000|
                #|SE_MSG_SET|xsm_ipv6_async_id_3|multinet_1-status 0x1a000000 0x1000000|
                # ...

                svc = s.split('xsm_')[1].split('_async_id_')[0]
                if v != '' and v != '(null)':

                    #print('svc=[' + svc + ']')
                    sbj = v.split()[0]
                    aid = v.split(' ', 1)[1]

                    function = ''
                    removed = False
                    for a in async_actions:
                        if a.split('|')[0] == aid:
                            function = a.split('|')[2]
                            break

                    if function == '':
                        #print('not found:', d)
                        continue

                    #print(s + ':' + svc, sbj)

                    index = next((index for (index, s) in enumerate(services) if s['name'] == svc), -1)
                    if index != -1:
                        services[index]['subjects'].append(sbj + ':' + function)

                        if function not in services[index]['functions']:
                            services[index]['functions'].append(function)

                    else:
                        service = {}
                        service['name'] = svc
                        service['subjects'] = [sbj + ':' + function]
                        service['functions'] = [function]
                        services.append(service)


    ############################################
    # build tples list
    #

    tples = []
    client = ''
    for d in debug:

        if d.split('|')[0] in ['OPEN_CONNECTION']:
            client = d.split('|')[1]

        ############################################
        elif d.split('|')[0] in ['SET']:

            subject = d.split('|')[1]
            value = d.split('|')[2]

            index = next((index for (index, d) in enumerate(tples) if d["subject"] == subject), -1)

            if index != -1:
                if tples[index]['subject'] != subject:
                    print('error')
                    exit()

                tples[index]['values'].append(value + ':' + client)

            else:
                tple = {}
                tple['subject'] = subject
                tple['values'] = [value + ':' + client]
                tple['options'] = []
                tple['gets'] = []
                tple['async_action'] = False
                tple['async_message'] = False
                tples.append(tple)


        ############################################
        elif d.split('|')[0] in ['SET_OPTIONS']:

            subject = d.split('|')[1]
            flags = d.split('|')[2]

            index = next((index for (index, d) in enumerate(tples) if d["subject"] == subject), -1)

            if index != -1:
                if tples[index]['subject'] != subject:
                    print('error')
                    exit()

                tples[index]['options'].append(flags + ':' + client)

            else:
                tple = {}
                tple['subject'] = subject
                tple['values'] = []
                tple['options'] = [flags + ':' + client]
                tple['gets'] = []
                tple['async_action'] = False
                tple['async_message'] = False
                tples.append(tple)



        ############################################
        elif d.split('|')[0] in ['SET_ASYNC_ACTION']:

            subject = d.split('|')[1]
            function = d.split('|')[2]
            flags = d.split('|')[3]

            index = next((index for (index, d) in enumerate(tples) if d['subject'] == subject), -1)

            if index != -1:
                if tples[index]['subject'] != subject:
                    print('error')
                    exit()
                tples[index]['async_action'] = True

            else:
                tple = {}
                tple['subject'] = subject
                tple['values'] = []
                tple['options'] = []
                tple['gets'] = []
                tple['async_action'] = True
                tple['async_message'] = False
                tples.append(tple)


        ############################################
        elif d.split('|')[0] in ['SET_ASYNC_MESSAGE']:

            subject = d.split('|')[1]

            index = next((index for (index, d) in enumerate(tples) if d['subject'] == subject), -1)

            if index != -1:
                if tples[index]['subject'] != subject:
                    print('error')
                    exit()
                tples[index]['async_message'] = True

            else:
                tple = {}
                tple['subject'] = subject
                tple['values'] = []
                tple['options'] = []
                tple['gets'] = []
                tple['async_action'] = False
                tple['async_message'] = True
                tples.append(tple)


        ############################################
        elif d.split('|')[0] in ['GET_REPLY']:

            subject = d.split('|')[1]
            value = d.split('|')[2]

            index = next((index for (index, d) in enumerate(tples) if d['subject'] == subject), -1)

            if index != -1:
                if tples[index]['subject'] != subject:
                    print('error')
                    exit()
                tples[index]['gets'].append(value + ':' + client)

            else:
                tple = {}
                tple['subject'] = subject
                tple['values'] = []
                tple['options'] = []
                tple['gets'] = [value + ':' + client]
                tple['async_action'] = False
                tple['async_message'] = False
                tples.append(tple)



    '''
    for service in services:
        for tple in tples:
            if tple['subject'] in service['subjects']:
                print(tple['asyncs'])
                for a in tple['asyncs']:
                    if a not in services[services.index(service)]['asyncs']:
                        services[services.index(service)]['asyncs'].append(a)
    '''

    #for s in services:
    #   print('name=',s['name'])
    #   print('subjects=', s['subjects'])
    #   print('functions=', s['functions'])
    #   print()


    #for t in sorted(tples, key=lambda x: x['subject'].lower()):
    #   print(t)


    #for c in clients:
    #   print(c)

    #for s in services:
    #   print('name=',s['name'])

    gen_html(clients, services, tples,async_messages, debug)
