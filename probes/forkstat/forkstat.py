#!/usr/bin/env python3

import sys, os, json, datetime, glob
from optparse import OptionParser
from urllib.parse import parse_qs, unquote

'''
import cProfile, pstats, io

def profile(fnc):

	def inner(*args, **kwargs):
		pr = cProfile.Profile()
		pr.enable()
		retval = fnc(*args, **kwargs)
		pr.disable()
		s = io.StringIO()
		sortby = 'cumulative'
		ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
		ps.print_stats()
		print(s.getvalue())
		return retval
	return inner
'''


landing_html = '''


<style type="text/css">
div.test
{
width:850px;
padding: 10px;
background: #f8f8f8;
border: 1px solid #d0d0d0;
border-radius: 10px;
}
</style>
</br>
<div class="test">
<select id="log" style="width:200px" disabled><option selected>date-target-cpu-length.log</option><select/></br>
</br>
&nbsp Select log file. Log files are named with a date / target / cpu / length. e.g. 60m = 60 minutes</br>
</br>
</br>
<select id="cmd" style="width:200px" disabled><option selected>None</option><select/></br>
</br>
&nbsp Select process from - log file based selection. To update selection for a new selected log, keep selection at None, and click Submit.</br>
</br>
</br>
<input type="text" id="custom" style="width:200px" name="custom" disabled></br>
</br>
&nbsp Custom specifier. Add comma separated process (paths) to be included with descendants. Add '-' to include without descendants.</br>
</br>
</br>
<input type="text" id="block" style="width:200px" name="block" disabled></br>
</br>
&nbsp Block specifier. Add comma separated process paths to be included or '-' excluded from the trace.</br>
</br>
</br>
<input type="checkbox" id="busybox name="busybox" disabled><label for="busybox">busybox</label>
<input type="checkbox" id="net" disabled><label for="net">net</label>
<input type="checkbox" id="iw" disabled><label for="iw">iw</label>
<input type="checkbox" id="cfg" disabled><label for="cfg">cfg</label></br>
</br>
&nbsp Include generic and (wireless-) networking utilities in the trace.</br>
</br>
</br>
<input type="checkbox" id="syscfg" disabled><label for="syscfg">syscfg</label>
<input type="checkbox" id="sysevent" disabled><label for="sysevent">sysevent</label>
<input type="checkbox" id="dmcli" disabled><label for="dmcli">dmcli</label>
<input type="checkbox" id="psmcli" disabled><label for="psmcli">psmcli</label>
<input type="checkbox" id="rpcclient" disabled><label for="rpcclient">rpcclient</label></br>
</br>
&nbsp Include these common utilities in the trace. If selected as a process, these will not show unless checked.</br>
</br>
</br>
<input type="checkbox" id="iw" disabled><label for="expand">expand</label></br>
</br>
&nbsp Show each unique process invokation on a separate line in the trace.</br>
</br>
</br>
<input type="submit" value= "Submit" disabled></br>
</br>
&nbsp Create a new trace from the selected log file for the selected process(es) and options.</br>
</br>
</br>
<b>In the trace..</b></br>
</br>
Scroll up to access the selection bar to make a new selection.</br>
Select a process by clicking on its event bar and see it's details in the lower section.</br>
In the lower section click the magnifying glass to open a new trace for that process.</br>

</div>
'''



mv1ofw_arm_busybox_bin = ['ash','busybox','cat','chattr','chmod','cp','cttyhack','date','dd','df','dmesg','dnsdomainname','dumpkmap','echo','false','grep','gunzip','gzip','hostname','ln','ls','mkdir','mknod','mktemp','more','mount','mv','netstat','nice','ping','ping6','pwd','rm','run-parts','sed','sleep','stat','stty','sync','tar','touch','true','umount','uname','usleep','vi']
mv1ofw_arm_busybox_sbin = ['arp','fdisk','fsck','getty','halt','hwclock','ifconfig','init','insmod','klogd','loadkmap','logread','lsmod','mdev','modprobe','poweroff','reboot','rmmod','route','runlevel','setconsole','start-stop-daemon','syslogd','udhcpc','vconfig','watchdog']
mv1ofw_arm_busybox_usr_bin =  ['[','[[','dc','du','nc','tr','wc','awk','cmp','cut','env','seq','tty','who','chvt','expr','find','head','sort','tail','test','tftp','time','uniq','wget','clear','flock','fuser','nohup','reset','users','which','xargs','logger','mkfifo','openvt','printf','renice','resize','setsid','telnet','hexdump','killall','logname','strings','basename','nslookup','readlink','realpath','deallocvt','crontab','traceroute','traceroute6']
mv1ofw_arm_busybox_usr_sbin = ['ntpd','crond','rdate','arping']



mv1ofw_atom_busybox_bin = ['ash','base64','cat','chgrp','chmod','chown','cp','cpio','date','df','dmesg','dnsdomainname','echo','ed','egrep','false','fgrep','getopt','grep','gunzip','gzip','hostname','iostat','ipcalc','kill','linux32','linux64','ln','ls','mkdir','mknod','mktemp','more','mount','mpstat','mv','netstat','nice','ping','ping6','pipe_progress','printenv','ps','pwd','rev','rm','rmdir','run-parts','sed','setarch','setserial','sleep','stat','stty','sync','tar','touch','true','umount','uname','uncompress','usleep','vi','watch','zcat']
mv1ofw_atom_busybox_sbin = ['adjtimex','arp','blockdev','busybox', 'fdisk','freeramdisk','fsck','fsck.minix','fstrim','getty','hdparm','hwclock','ifconfig','ifdown','ifup','insmod','ipaddr','iplink','iproute','iprule','iptunnel','klogd','loadkmap','logread','losetup','lsmod','makedevs','mkfs.minix','mkswap','modprobe','nameif','pivot_root','rmmod','route','setconsole','slattach','start-stop-daemon','sulogin','swapoff','swapon','switch_root','sysctl','syslogd','udhcpc','vconfig','zcip']
mv1ofw_atom_busybox_usr_bin = ['[','[[','ar','awk','basename','bunzip2','bzcat','bzip2','cal','chpst','chrt','chvt','cksum','clear','cmp','comm','cut','dc','deallocvt','diff','dirname','dos2unix','du','env','envdir','envuidgid','expand','expr','fgconsole','find','flock','fold','free','fuser','head','hexdump','hostid','id','ipcrm','ipcs','killall','less','logger','logname','lsof','lspci','lsusb','lzcat','lzma','md5sum','microcom','mkfifo','nmeter','nohup','openvt','pgrep','pkill','printf','pstree','pwdx','readlink','realpath','renice','reset','rpm2cpio','runsv','runsvdir','rx','script','seq','setsid','sha1sum','sha3sum','smemcap','softlimit','sort','split','strings','sum','sv','tac','tail','taskset','tee','test','tftp','time','top','tr','traceroute','tty','ttysize','udpsvd','unexpand','uniq','unix2dos','unlzma','unxz','unzip','uptime','users','uudecode','uuencode','vlock','wc','wget','which','who','whoami','whois','xargs','xz','xzcat','yes']
mv1ofw_atom_busybox_usr_sbin = ['addgroup','adduser','arping','brctl','chroot','delgroup','deluser','fbset','inetd','killall5','loadfont','ntpd','powertop','rdate','readahead','rfkill','setlogcons','svlogd','tftpd','ubiattach','ubidetach','ubimkvol','ubirmvol','ubirsvol','ubiupdatevol']

mv1ofw_arm_procps = ['free','kill','pgrep','pidof','pkill','pmap','ps','pwdx','skill','snice','sysctl','top','uptime','w','watch']
mv1ofw_arm_shadow = ['login','su']
mv1ofw_arm_bash = ['bash','sh']

mv1ofw_atom_sysvinit = ['halt','init','last','mesg','mountpoint','pidof','poweroff','reboot','runlevel','shutdown','utmpdump','wall']



combinelist = []
combinelist+= ['swctl *', 'ifconfig *', 'vconfig *', 'mount *', 'ln *', 'date *', 'rm *', 'cat *', 'iwconfig *', 'iwpriv *', 'iwlist *', 'cfg *', 'touch *', '/bin/touch *', 'ip *']

combinelist+= ['execute_dir *']

#combinelist+= ['sysevent async *']
#combinelist+= ['sysevent set *']
#combinelist+= ['sysevent get *']
combinelist+= ['sysevent .']

combinelist+= ['syscfg .']


combinelist+= ['service_dhcp .']
combinelist+= ['service_multinet_exec *']
combinelist+= ['/usr/bin/firewall *']
combinelist+= ['service_routed *']
combinelist+= ['service_dslite *']
combinelist+= ['service_ipv6 *']
combinelist+= ['service_udhcpc *']
combinelist+= ['service_wan *']


combinelist+= ['/bin/sh /etc/utopia/service.d/firewall_log_handle.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_ccsphs.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_dhcp_server.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_dhcpv6_client.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_ipv6.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_mcastproxy.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_igd.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_misc.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_mldproxy.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_potd.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_radiusrelay.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_routed.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/service_wan.sh *']

combinelist+= ['/bin/sh /etc/utopia/service.d/service_ipv4.sh *']
combinelist+= ['/bin/sh /etc/utopia/service.d/lan_handler.sh *']

combinelist+= ['dibbler-client *']
combinelist+= ['dibbler-server *']

combinelist+= ['/sbin/modprobe *']

combinelist+= ['rpcclient *']
combinelist+= ['/usr/bin/rpcclient *']

combinelist+= ['/sbin/udhcpc *']
combinelist+= ['/bin/sh /etc/udhcpc.script *']

combinelist+= ['print_uptime *']

combinelist+= ['sleep *']

combinelist+= ['nice -n *']


#atom

#combinelist+= ['/bin/init_man *']
#combinelist+= ['/etc/Wireless/CL2330/hostapd *']

#combinelist+= ['/bin/sh /etc/Wireless/CL2330/nvram_set *']
#combinelist+= ['/bin/sh /etc/Wireless/CL2330/nvram_get *']
#combinelist+= ['/bin/sh /etc/Wireless/CL242/nvram_set *']
#combinelist+= ['/bin/sh /etc/Wireless/CL242/nvram_get *']

combinelist+= ['mknod *']
combinelist+= ['insmod *']
combinelist+= ['killall *']

#combinelist+= ['dmcli *']

# keep these at the end
combinelist+= ['sh -c sh .', 'sh -c .', 'sh .']
combinelist+= ['/bin/sh -c .', '/bin/sh .']
combinelist+= ['/bin/bash -c .', '/bin/bash .']




def fixup(s):
	for c in s:
		if not c.isprintable():
			s = s.replace(c, '?')

	return s.replace('\\', '\\\\').replace('"','\\"').replace('\\\\n', '\\n')


meta_thread_name_printed = []
meta_thread_sort_index_printed = []
meta_process_name_printed = []
meta_process_sort_index_printed = []


def printevent(key, data, cmd, cmds, fullcmd, start, end, masterpid_index, masterpid_name, masterpid_pid, f):

	printevent.counter+= 1

	id = cmds.index(cmd)
	tid = str(key)
	name = cmd
	fullname = tid + ' ' + fullcmd
	marker = ''
	if 'clone_ts' in data[key]:
		marker = ' * '
	elif 'exec_ts' not in data[key]:
		marker = ' - '
	ts = float(start) * 1.0e6
	dur = float(end) * 1.0e6 - ts
	if dur < 0:
		dur = 1

	tree_pidscmds = familytree(data, key)

	parents = fixup('\\n'.join(tree_pidscmds))
	if 'clone_ts' in data[key]:
		args = '{"Thread":"","Parents":"%s"}' %(parents)
	else:
		nr_forks = data[key]['nr_forks'] if 'nr_forks' in data[key] else 0
		nr_threads = data[key]['nr_threads'] if 'nr_threads' in data[key] else 0
		args = '{"Process":"%d fork(s), %d thread(s)","Parents":"%s"}' %(nr_forks, nr_threads, parents)

	if printevent.counter == 1:
		line = '{"ph":"X","pid":"%d","tid":%d,"name":"%s","ts":%d,"dur":%d,"args":%s},' %(masterpid_pid, id, fixup(fullname) + marker, 0.0, 1, args)
		print(line, file = f)

	line = '{"ph":"X","pid":"%d","tid":%d,"name":"%s","ts":%d,"dur":%d,"args":%s},' %(masterpid_pid, id, fixup(fullname) + marker, ts, dur, args)
	print(line, file = f)


	if not id in meta_thread_name_printed:
		print('{"name":"thread_name","ph":"M","pid":"%d","tid":%d,"args":{"name":"%s"}},' %(masterpid_pid, id, fixup(name)))
		meta_thread_name_printed.append(id)

	if not id in meta_thread_sort_index_printed:
		print('{"name":"thread_sort_index","ph":"M","pid":"%d","tid":%d,"args":{"sort_index":%d}},' %(masterpid_pid, id, id))
		meta_thread_sort_index_printed.append(id)

	if not masterpid_name in meta_process_name_printed:
		print('{"name":"process_name","ph":"M","pid":"%d","args":{"name":"%s"}},' %(masterpid_pid, masterpid_name))
		meta_process_name_printed.append(masterpid_name)

	if not masterpid_index in meta_process_sort_index_printed:
		print('{"name":"process_sort_index","ph":"M","pid":"%d","args":{"sort_index":%d}},' %(masterpid_pid, masterpid_index))
		meta_process_sort_index_printed.append(masterpid_index)


def genallevents(data, masterpid_index, masterpid_name, masterpid_pid, all_children_positive_map, f, combine, block):

	global meta_thread_name_printed
	global meta_thread_sort_index_printed
	global meta_process_name_printed
	global meta_process_sort_index_printed


	#sys.stderr.write('writing trace events, ' + str(len(data)) + ' total pids, ' + str(len(all_children_positive)) + ' positive descendants, ' + str(len(all_children_negative)) + ' negative descendants.. (combine==%s)\n' %("False" if not combine else "True"))
	sys.stderr.write('writing trace events..\n')


	#sys.stderr.write('block=\n')
	#for b in block:
	#	sys.stderr.write(b + '\n')


	highest_ts = 0.0;
	for key in data:
		for ts in ['exec_ts', 'fork_ts', 'clone_ts', 'exit_ts', 'sid_ts', 'uid_ts']:
			if ts in data[key]:
				if float(data[key][ts]) > highest_ts:
					highest_ts = float(data[key][ts])

	meta_thread_name_printed = []
	meta_thread_sort_index_printed = []

	meta_process_name_printed = []
	meta_process_sort_index_printed = []

	printevent.counter = 0

	cmds = []

	if block:
		blocklist1 = tuple([x + ' ' for x in block])
		blocklist2 = tuple(['sh -c ' + x + ' ' for x in block])

	for key in data:

		if masterpid_pid != 0:
			if all_children_positive_map[key] == 0:
				continue


		if any(item in ['fork_ts', 'exec_ts', 'clone_ts'] for item in data[key]):

			if 'cmd' in data[key]:

				#sys.stderr.write(data[key]['cmd'] + '\n')

				if block:

					if data[key]['cmd'] in block:
						#sys.stderr.write('block1\n')
						continue

					#if data[key]['cmd'].startswith(tuple([x + ' ' for x in block])):
					if data[key]['cmd'].startswith(blocklist1):
						#sys.stderr.write('block2\n')
						continue

					#if data[key]['cmd'].startswith(tuple(['sh -c ' + x + ' ' for x in block])):
					if data[key]['cmd'].startswith(blocklist2):
						#sys.stderr.write('block3\n')
						continue


				fullcmd = data[key]['cmd']

				#if combine and not ';' in fullcmd:
				if combine:

					cmd = fullcmd.split()[0]

					for n in combinelist:

						if n.split()[0] == fullcmd.split()[0]:

							j = 0
							for i in range(len(n.split())):

								if i == len(fullcmd.split()):
									break
								elif n.split()[i] == '.' or n.split()[i] == fullcmd.split()[i]:
									j+= 1
								elif n.split()[i] == '*':
									j = len(fullcmd.split())
									break
								else:
									j = 0
									break

							if j > 0:
								cmd = ' '.join(fullcmd.split()[0:j])
								break;


				else:

					cmd = fullcmd

				#sys.stderr.write('cmd=' + cmd  + '\n')

				if cmd not in cmds:
					cmds.append(cmd)


				# take exec_ts over fork_ts
				# take fork_ts if there is no exec_ts
				if 'exec_ts' in data[key]:
					ts = data[key]['exec_ts']
				elif 'fork_ts' in data[key]:
					ts = data[key]['fork_ts']
				elif 'clone_ts' in data[key]:
					ts = data[key]['clone_ts']
				else:
					sys.stderr.write('unknown ts for pid :' + key  + '\n')

				printevent(key, data, cmd, cmds, fullcmd, ts, highest_ts if 'exit_ts' not in data[key] else data[key]['exit_ts'], masterpid_index, masterpid_name, masterpid_pid, f)

			else:
				sys.stderr.write('internal error: no cmd, exiting\n')
				exit(1)

		else:
			sys.stderr.write('internal error: no exec/fork/clone, exiting\n')
			exit(1)


def match(sub, s):

	if sub == s:
		return True

	elif '/bin/sh -c ' + sub == s:
		return True
	elif '/bin/sh ' + sub == s:
		return True
	elif '/bin/bash ' + sub == s:
		return True
	elif 'sh ' + sub == s:
		return True
	elif 'sh -c ' + sub == s:
		return True
	elif 'sh -c sh ' + sub == s:
		return True

	elif s.startswith(sub + ' '):
		return True
	elif s.startswith('/bin/sh -c ' + sub + ' '):
		return True
	elif s.startswith('/bin/sh ' + sub + ' '):
		return True
	elif s.startswith('/bin/bash ' + sub + ' '):
		return True
	elif s.startswith('sh ' + sub + ' '):
		return True
	elif s.startswith('sh -c ' + sub + ' '):
		return True
	elif s.startswith('sh -c sh ' + sub + ' '):
		return True
	elif sub + ' ' in s:
		return True

	return False


def find_all_children(data, pidchildren, masterpid_cmds):

	masterpid_pid = 0

	firstpid = True
	masterpids = []
	for key in data:
		if 'cmd' in data[key] and 'clone_ts' not in data[key]:
			for mc in masterpid_cmds:

				if mc == 'None':
					continue

				if mc == 'All' or match(mc, data[key]['cmd']):

					if firstpid:
						masterpid_pid = key
						firstpid = False
					masterpids.append(key)

	#sys.stderr.write('masterpid_pid=' + str(masterpid_pid) + '\n')
	#sys.stderr.write('masterpids=' + ','.join([str(i) for i in masterpids]) + '\n')


	all_children = []

	parentshandled = [0] * 20 * 100000

	parents = []
	for p in masterpids:
		parents.append(p)

	while True:
		newparents = []
		foundmore = False
		for p in parents:
			if parentshandled[p] == 0 and p in pidchildren:
				for pp in pidchildren[p]:
					newparents.append(pp)

					#sys.stderr.write('add:' + str(pp) + '\n')

					all_children.append(pp)

					foundmore = True
				parentshandled[p] = 1
		for np in newparents:
			if parentshandled[np] == 0:
				parents.append(np)

		if not foundmore:
			break

	for c in masterpids:
		if not c in all_children:
			#sys.stderr.write('add ' + c + '\n')
			all_children.append(c)

	return masterpid_pid, masterpids, all_children


def process_lines_for_corruption(lines):

	corruptlines = []
	i = 0
	while i < len(lines):

		if ' fork ' in lines[i] and ' parent ' in lines[i] and ' fork ' in lines[i + 1] and ' child ' in lines[i + 1]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			if len(lines[i + 1].split(None, 4)) != 5:
				corruptlines.append(lines[i + 1][:-1])
			i+= 2

		elif ' exec ' in lines[i]:
			if len(lines[i].split(None, 3)) != 4:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' exit ' in lines[i]:
			if len(lines[i].split(None, 2)) != 3:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' clone ' in lines[i] and ' parent ' in lines[i] and ' clone ' in lines[i + 1] and ' thread ' in lines[i + 1]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			if len(lines[i + 1].split(None, 4)) != 5:
				corruptlines.append(lines[i + 1][:-1])
			i+= 2

		elif ' sid ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' uid ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' comm ' in lines[i]:
			if len(lines[i].split(None, 3)) != 4:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' ptrce ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			i+= 1

		elif ' core ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(lines[i][:-1])
			i+= 1

		else:
			corruptlines.append(lines[i][:-1])
			corruptlines.append(lines[i + 1][:-1])

	return corruptlines


def log2data(infile):

	lines = []
	with open(infile, 'r', encoding = 'ascii', errors = 'ignore') as fp:
		lines = fp.readlines()

	if not lines:
		sys.stderr.write('empty file \"%s\" \n' %(infile))
		return []


	sys.stderr.write('parsing \"%s\" %d lines..\n' %(infile, len(lines)))

	'''
	# chop off anything beyond pid 32700
	l = len(lines)
	i = l
	for line in lines:
		i-= 1
		items = line.split()
		if int(items[2]) > 32700:
			break;

	for j in range(i):
		lines.pop()

	if i > 0:
		sys.stderr.write('%d lines; popped %d lines; remain %d lines\n' %(l, i, len(lines)))
	'''


	# chop off last bit of input log
	# based on finding 2x exit
	i = 0
	n = 0
	for line in reversed(lines):
		items = line.split()
		if len(items) == 3 and items[1] == 'exit':
			n+= 1
			if n == 2:
				break
		i+= 1
	for n in range(i):
		lines.pop()


	# chop off first bit of input log
	# based on anything thats not a fork + parent
	i = 0
	for line in lines:
		items = line.split()
		if items[1] == 'fork' and items[3] == 'parent':
			firstchild = 0
			break
		i+= 1
	for n in range(i):
		lines.pop(0)


	# check for time jumps
	prev_time = 0.0
	for line in lines:
		#print(line)
		time = float(line.split()[0])
		if prev_time == 0:
			prev_time = time
		if abs(time - prev_time) > 3600:
			sys.stderr.write('jump ' + line +'\nexiting\n')
			exit(1)
		prev_time = time


	# check for corrupt lines
	corruptlines = process_lines_for_corruption(lines)
	if corruptlines:
		for line in corruptlines:
			sys.stderr.write('corruptline: [' + line + ']\n')
		#sys.stderr.write('exiting\n')
		#exit(1)


	# in this section deal with fact that pids are recycled within '0-32767'
	#
	#
	# for new pids  (fork 'pid' child / clone 'pid' thread)
	#
	#   if pid not in pids_ever then keep same
	#   if pid in pids_ever then replace with bumped
	#
	#
	# for active pids  (fork 'pid' parent / clone 'pid' parent / exec 'pid' /exit 'pid' / sid / uid / comm / core / ptrce)
	#
	#   if pid in pids_active then keep same
	#   if pid not in pids_active then replace with the bumped in pids_active

	# the first two lines should always be fork parent + fork child
	# determine the first child seen from this
	if ' fork ' in lines[0] and ' parent ' in lines[0] and ' fork ' in lines[1] and ' child ' in lines[1]:
		firstchild = int(lines[1].split(None, 3)[2])
	else:
		sys.stderr.write('unexpected start lines\nexiting\n')
		exit(1)

	MOD = 100000

	# 0 = not seen
	# n = seen n times
	# set unseen to 1 in ever
	pids_ever = [0] * MOD
	for i in range(firstchild):
		pids_ever[i] = 1

	# 0 = not active 
	# 1 = active
	# set unseen in active
	pids_active = [0] * MOD
	for i in range(firstchild):
		pids_active[i] = 1

	i = 0
	while i < len(lines):

		if ' fork ' in lines[i] and ' parent ' in lines[i] and ' fork ' in lines[i + 1] and ' child ' in lines[i + 1]:
			parentpid = lines[i].split(None, 3)[2]
			childpid = lines[i + 1].split(None, 3)[2]


			if pids_active[int(parentpid)] == 0:
				sys.stderr.write('parentpid \"fork\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			if pids_active[int(childpid)] != 0:
				#this is ok
				#sys.stderr.write('childpid \"fork\", while in active_pids: [' + lines[i + 1][:-1] + ']\n')
				pass

			pids_active[int(childpid)] = 1
			pids_ever[int(childpid)] += 1

			# bump parentpid?
			if pids_ever[int(parentpid)] > 1:
				lines[i] = lines[i].replace(' ' + parentpid + ' ', ' ' + str(int(parentpid) + (pids_ever[int(parentpid)] - 1) * MOD) + ' ')

			# bump childpid?
			if pids_ever[int(childpid)] > 1:
				lines[i + 1] = lines[i + 1].replace(' ' + childpid + ' ', ' ' + str(int(childpid) + (pids_ever[int(childpid)] - 1) * MOD) + ' ')

			i+= 2


		elif ' exec ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"exec\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] - 1) * MOD) + ' ')

			i+= 1


		elif ' exit ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"exit\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			pids_active[int(pid)] = 0

			# bump pid?
			#### specific replace pattern :  ' ' + pid - no second ' '
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid, ' ' + str(int(pid) + (pids_ever[int(pid)] - 1) * MOD))

			i+= 1


		elif ' clone ' in lines[i] and ' parent ' in lines[i] and ' clone ' in lines[i + 1] and ' thread ' in lines[i + 1]:
			parentpid = lines[i].split(None, 3)[2]
			childpid = lines[i + 1].split(None, 3)[2]

			if pids_active[int(parentpid)] == 0:
				sys.stderr.write('parentpid \"clone\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			if pids_active[int(childpid)] != 0:
				#this is ok
				#sys.stderr.write('childpid \"clone\"" while in active_pids: [' + lines[i + 1][:-1] + ']\n')
				pass


			pids_active[int(childpid)] = 1
			pids_ever[int(childpid)] += 1

			# bump parentpid?
			if pids_ever[int(parentpid)] > 1:
				lines[i] = lines[i].replace(' ' + parentpid + ' ', ' ' + str(int(parentpid) + (pids_ever[int(parentpid)] -1) * MOD) + ' ')

			# bump childpid?
			if pids_ever[int(childpid)] > 1:
				lines[i + 1] = lines[i + 1].replace(' ' + childpid + ' ', ' ' + str(int(childpid) + (pids_ever[int(childpid)] - 1) * MOD) + ' ')

			i+= 2


		elif ' sid ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"sid\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] - 1) * MOD) + ' ')

			i+= 1


		elif ' uid ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"uid\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] - 1) * MOD) + ' ')

			i+= 1


		elif ' comm ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"comm\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] - 1) * MOD) + ' ')

			i+= 1


		elif ' ptrce ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"ptrce\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] -1) * MOD) + ' ')

			i+= 1


		elif ' core ' in lines[i]:
			pid = lines[i].split(None, 3)[2]

			if pids_active[int(pid)] == 0:
				sys.stderr.write('pid \"core\", while not in active_pids: [' + lines[i][:-1] + ']\n')
				pass

			# bump pid?
			if pids_ever[int(pid)] > 1:
				lines[i] = lines[i].replace(' ' + pid + ' ', ' ' + str(int(pid) + (pids_ever[int(pid)] -1) * MOD) + ' ')

			i+= 1


		else:
			sys.stderr.write([i][:-1] + '\n')
			sys.stderr.write([i+1][:-1] + '\n')
			sys.stderr.write('internal error, exiting\n')
			exit(1)


	#with open('./lines.txt', 'w') as out_file:
	#	for line in lines:
	#		out_file.write(line)


	ppid1_cmds = []
	data = {}
	i = 0
	while i < len(lines):

		items = lines[i].split()
		items1 = '' if (i + 1) == len(lines) else lines[i + 1].split()

		if items[1] == 'fork' and items[3] == 'parent' and items1[1] == 'fork' and items1[3] == 'child' :
			ppid = int(items[2])
			pid = int(items1[2])

			data[pid] = {}
			data[pid]['nr_forks'] = 0
			data[pid]['nr_execs'] = 0
			data[pid]['execs'] = []
			data[pid]['nr_threads'] = 0
			data[pid]['fork_ts'] = str(float(items1[0]))
			data[pid]['parent_pid'] = ppid
			data[pid]['parent_cmd'] = ' '.join(items[4:])
			data[pid]['cmd'] = ' '.join(items1[4:])

			if ppid in data:
				data[ppid]['nr_forks']+= 1


			if ppid == 1 and data[pid]['cmd'] != '/sbin/init' and data[pid]['cmd'] != 'init [5]':
				#sys.stderr.write('\tparentpid = 1, pid = %d, %s\n'%(pid, data[pid]['cmd']))

				if data[pid]['cmd'] not in ppid1_cmds:
					ppid1_cmds.append(data[pid]['cmd'])

				previous_matching_exec_line = ''
				#look back max 500 lines to see if there was an 'exec' with that cmd
				for n,j in enumerate(reversed(range(i + 1))):
					if n == 500:
						break
					jtems = lines[j].split()
					if jtems[1] == 'exec' and data[pid]['cmd'] in ' '.join(jtems[3:]):
						previous_matching_exec_line = lines[j][:-1]
						break

				previous_matching_fork_line = ''
				#look back max 500 lines to see if there was an 'exec' with that cmd
				for n,j in enumerate(reversed(range(i + 1))):
					if n == 500:
						break
					jtems = lines[j].split()
					if jtems[1] == 'fork' and jtems[3] == 'child' and data[pid]['cmd'] in ' '.join(jtems[4:]):
						previous_matching_fork_line = lines[j][:-1]
						break

				next_exit_line = ''
				#look forward max 500 lines to the next 'exit'
				for n,j in enumerate(range(i, len(lines))):
					if n == 500:
						break
					jtems = lines[j].split()
					if jtems[1] == 'exit':
						next_exit_line = lines[j][:-1]
						break

				#sys.stderr.write('   previous_matching_exec_line: %s\n'%(previous_matching_exec_line))
				#sys.stderr.write('   previous_matching_fork_line: %s\n'%(previous_matching_fork_line))
				#sys.stderr.write('   next_exit_line: %s\n'%(next_exit_line))

				if not next_exit_line:
					sys.stderr.write('no next exit line, internal error, exiting\n')
					exit(1)

				next_exit_line_pid = next_exit_line.split()[2]

				if previous_matching_exec_line and previous_matching_exec_line.split()[2] == next_exit_line_pid:
					#sys.stderr.write('\tprevious exec pid (%s) == next exit pid (%s)\n' %(previous_matching_exec_line.split()[2], next_exit_line_pid))
					#sys.stderr.write('\t(%d)parent_pid rewritten (%d)<-(%d), parent_cmd rewritten (%s)<-(%s)\n' %(pid, data[pid]['parent_pid'], int(previous_matching_exec_line.split()[2]), data[pid]['parent_cmd'], ' '.join(previous_matching_exec_line.split()[3:])))
					data[pid]['parent_pid'] = int(previous_matching_exec_line.split()[2])
					data[pid]['parent_cmd'] = ' '.join(previous_matching_exec_line.split()[3:])
				elif previous_matching_fork_line and previous_matching_fork_line.split()[2] == next_exit_line_pid:
					#sys.stderr.write('\tprevious fork pid (%s) == next exit pid (%s)\n' %(previous_matching_fork_line.split()[2], next_exit_line_pid))
					#sys.stderr.write('\t(%d)parent_pid rewritten (%d)<-(%d), parent_cmd rewritten (%s)<-(%s)\n' %(pid, data[pid]['parent_pid'], int(previous_matching_fork_line.split()[2]), data[pid]['parent_cmd'], ' '.join(previous_matching_fork_line.split()[4:])))
					data[pid]['parent_pid'] = int(previous_matching_fork_line.split()[2])
					data[pid]['parent_cmd'] = ' '.join(previous_matching_fork_line.split()[4:])
				else:
					#sys.stderr.write('\tprevious exec pid (%s) / fork pid (%s) != next exit pid (%s)\n' %(previous_matching_exec_line.split()[2] if previous_matching_exec_line else '?', previous_matching_fork_line.split()[2] if previous_matching_fork_line else '?', next_exit_line_pid))

					previous_matching_pid_line = ''
					#look back max 100 lines to see if there was an 'exec' or 'fork' for that pid
					for n,j in enumerate(reversed(range(i + 1))):
						if n == 100:
							break
						jtems = lines[j].split()
						if jtems[2] == next_exit_line.split()[2] and (jtems[1] == 'fork' or jtems[1] == 'exec'):
							previous_matching_pid_line = lines[j][:-1]
							break

					oldparentcmd = data[pid]['parent_cmd']
					if previous_matching_pid_line:
						if ' fork ' in previous_matching_pid_line and next_exit_line.split()[2] == previous_matching_pid_line.split()[2]:
							data[pid]['parent_cmd'] = ' '.join(previous_matching_pid_line.split()[4:])
						elif ' exec ' in previous_matching_pid_line and next_exit_line.split()[2] == previous_matching_pid_line.split()[2]:
							data[pid]['parent_cmd'] = ' '.join(previous_matching_pid_line.split()[3:])
						else:
							sys.stderr.write('determining parent pid, internal error, exiting\n')
							exit(1)

						#sys.stderr.write('\t(%d)parent_pid rewritten (%d)<-(%d), parent_cmd rewritten (%s)<-(%s)\n' %(pid, data[pid]['parent_pid'], int(next_exit_line.split()[2]), oldparentcmd, data[pid]['parent_cmd']))
						data[pid]['parent_pid'] = int(next_exit_line.split()[2])

					else:
						#sys.stderr.write(lines[i][:-1] + '\n')
						#sys.stderr.write(lines[i + 1][:-1] + '\n')
						#sys.stderr.write('internal error, exiting\n')
						#exit(1)
						pass

			i+= 2


		elif items[1] == 'exec':
			pid = int(items[2])

			if pid in data:
				data[pid]['exec_ts'] = str(float(items[0]))
				data[pid]['cmd'] = ' '.join(items[3:])
				data[pid]['nr_execs']+= 1
				data[pid]['execs'].append(' '.join(items[3:]))
			i+= 1


		elif items[1] == 'exit':
			pid = int(items[2])

			if pid in data:
				data[pid]['exit_ts'] = str(float(items[0]))

			i+= 1


		elif items[1] == 'clone' and items[3] == 'parent' and items1[1] == 'clone' and items1[3] == 'thread' :
			ppid = int(items[2])
			pid = int(items1[2])

			data[pid] = {}
			data[pid]['nr_forks'] = 0
			data[pid]['nr_execs'] = 0
			data[pid]['execs'] = []
			data[pid]['nr_threads'] = 0
			data[pid]['clone_ts'] = str(float(items1[0]))
			data[pid]['parent_pid'] = ppid
			data[pid]['parent_cmd'] = ' '.join(items[4:])
			data[pid]['cmd'] = ' '.join(items1[4:])

			if ppid in data:
				data[ppid]['nr_threads']+= 1

			i+= 2


		elif items[1] == 'sid':
			pid = int(lines[i].split(None, 3)[2])
			if pid in data:
				data[pid]['sid_ts'] = str(float(items[0]))

			#sys.stderr.write('sid, %d, %s\n'%(pid, lines[i][:-1]))

			i+= 1
		elif items[1] == 'uid':
			pid = int(lines[i].split(None, 3)[2])
			if pid in data:
				data[pid]['uid_ts'] = str(float(items[0]))
			i+= 1
		elif items[1] == 'comm':
			pid = int(lines[i].split(None, 3)[2])
			if pid in data:
				data[pid]['comm_ts'] = str(float(items[0]))
			i+= 1
		elif items[1] == 'ptrce':
			pid = int(lines[i].split(None, 3)[2])
			if pid in data:
				data[pid]['ptrce_ts'] = str(float(items[0]))
			i+= 1
		elif items[1] == 'core':
			pid = int(lines[i].split(None, 3)[2])
			if pid in data:
				data[pid]['core_ts'] = str(float(items[0]))
			i+= 1

		else:
			sys.stderr.write(lines[i][:-1] + '\n')
			sys.stderr.write('internal error, exiting\n')
			exit(1)


	sys.stderr.write('%d processes with parent pid 1:\n' %(len(ppid1_cmds)))
	#sys.stderr.write('%s, %d processes with parent pid 1:\n' %(infile, len(ppid1_cmds)))
	#for count, ppid1_cmd in enumerate(sorted(ppid1_cmds)):
	#	sys.stderr.write('%2d \"%s\"\n'%(count, ppid1_cmd))

	return data


def fromquerystring(querystring, subquery):

	if querystring:
		qs = parse_qs(unquote(unquote(querystring)))
		for key in qs:
			if key == subquery:
				return ','.join(qs[key])
	return ''


def familytree(data, pid):

	tree_pidscmds = []
	parent = pid
	while parent in data:
		#sys.stderr.write('parent=' + str(parent) + '\n')
		tree_pidscmds.append(str(data[parent]['parent_pid']) + ' ' + data[parent]['parent_cmd'])
		parent = data[parent]['parent_pid']

	return tree_pidscmds


def writeresults(data, options, f, combine):

	print('{"otherData": {},"traceEvents":[', file = f)

	mastercmds = []

	block = []
	block.append('<unknown>')
	block.extend(['[kworker/u2:1]', '[kworker/u4:0]', '[kthreadd]', '[kjournald]'])

	if fromquerystring(options.querystring, 'busybox') != 'yes':
		block.extend(set(mv1ofw_arm_busybox_sbin + mv1ofw_arm_busybox_bin + mv1ofw_arm_busybox_usr_sbin + mv1ofw_arm_busybox_usr_bin))
		block.extend(set(mv1ofw_atom_busybox_sbin + mv1ofw_atom_busybox_bin + mv1ofw_atom_busybox_usr_sbin + mv1ofw_atom_busybox_usr_bin))
		block.append('brpath=$(readlink')
		block.extend(set(mv1ofw_arm_procps + mv1ofw_arm_shadow + mv1ofw_atom_sysvinit))


	#block.extend(['ifconfig', 'sed', 'cat', 'rm', 'busybox', 'vconfig', 'cut', 'awk', 'echo', 'grep', 'pidof', 'brctl'])


	if fromquerystring(options.querystring, 'net') != 'yes':
		block.extend(['ip', 'iptables','ip6tables','iptables-save','ip6tables-save','iptables-restore', 'ip6tables-restore', 'ebtables', 'conntrack', 'swctl'])

	if fromquerystring(options.querystring, 'iw') != 'yes':
		block.extend(['iw', 'iwscan', 'iwpriv', 'iwconfig', 'iwlist', 'iwgetid', 'iwspy'])

	for cmd in ['syscfg', 'sysevent', '/usr/bin/sysevent', 'dmcli', 'psmcli', 'rpcclient', '/usr/bin/rpcclient', 'cfg']:
		if fromquerystring(options.querystring, cmd) != 'yes':
			block.append(cmd)

	if options.querystring:
		qsblock = fromquerystring(options.querystring, 'block')
		if qsblock:
			sys.stderr.write('options.querystring(block)=' + fromquerystring(options.querystring, 'block') + '\n')
			for b in qsblock.split(','):
				if b.startswith('-'):
					block.append(b[1:])
				else:
					while b in block:
						sys.stderr.write('removing %s from block \n' %(b))
						block.remove(b)


	if options.querystring:

		sys.stderr.write('options.querystring(raw)=\"' + options.querystring + '\"\n')
		sys.stderr.write('options.querystring(parse_qs)=\"' + ','.join(parse_qs(options.querystring)) + '\"\n')

		qs = parse_qs(unquote(unquote(options.querystring)))

		#sys.stderr.write('options.querystring(parse_qs(unquote(unquote()))=\n')
		#for key in qs:
		#	sys.stderr.write(key + ':' + ','.join(qs[key]) + '\n')

		for key in qs:
			if key == 'cmd':
				mastercmds.append(key + '=' + ','.join(qs[key]) + ((',' + fromquerystring(options.querystring, 'custom')) if fromquerystring(options.querystring, 'custom') else ''))

	elif options.mastercmds:

		mastercmds = options.mastercmds

	sys.stderr.write('master_cmds=' + ','.join(mastercmds) + '\n')

	if mastercmds:

		if 'cmd=All' in mastercmds:
			genallevents(data, 0, 'ALL', 0, [], f, combine, block)

		elif 'cmd=None' in mastercmds:
			pass

		else:
			pidchildren = {}
			for key in data:
				if data[key]['parent_pid'] in data:

					if data[key]['parent_cmd'] != data[ data[key]['parent_pid'] ]['cmd']:
						#sys.stderr.write('parent_cmd != parent_pidcmd : (%s) != (%s)\n' %(data[key]['parent_cmd'].ljust(60), data[ data[key]['parent_pid'] ]['cmd'].ljust(60)))
						#continue
						pass

				if not data[key]['parent_pid'] in pidchildren:
					pidchildren[data[key]['parent_pid']] = []
				pidchildren[data[key]['parent_pid']].append(key)

			for mp in mastercmds:

				sys.stderr.write('finding descendants, \"' + mp + '\"' + ', ' + str(len(data)) + ' pids..\n')

				masterpid_name = mp.split('=')[0].replace('\'','')
				masterpid_cmds = mp.split('=')[1].replace('\'','').split(',')

				sys.stderr.write('masterpid_name=' + masterpid_name + '\n')
				sys.stderr.write('masterpid_cmds=' + ','.join(masterpid_cmds) + '\n')


				all_children_positive_map = [0] * 20 * 100000

				the_masterpid_pid_positive = 0


				for mc in masterpid_cmds:

					sys.stderr.write('masterpid_cmd=' + mc + '\n')

					all_children_positive = []
					all_children_negative = []

					if not mc.startswith('-'):

						masterpid_pid_positive, masterpid_pids_positive, all_children_positive = find_all_children(data, pidchildren, [mc])
						if the_masterpid_pid_positive == 0:
							the_masterpid_pid_positive = masterpid_pid_positive

						for c in all_children_positive:
							all_children_positive_map[c] = 1

					else:
						masterpid_pid_negative, masterpid_pids_negative, all_children_negative = find_all_children(data, pidchildren, [mc[1:]])

						sys.stderr.write('masterpid_pid_negative=' + str(masterpid_pid_negative) + '\n')
						sys.stderr.write('masterpid_pids_negative=' + ','.join([str(i) for i in masterpid_pids_negative]) + '\n')


						for c in all_children_negative:
							all_children_positive_map[c] = 0

						# only disallow descendants
						for c in masterpid_pids_negative:
							all_children_positive_map[c] = 1

					sys.stderr.write('all_children_positive: ' + str(len(all_children_positive)) + ', all_children_negative: ' + str(len(all_children_negative)) + '\n')

					'''
					if 1231 in all_children_negative:
						sys.stderr.write('1231 in all_children_negative' + '\n')
					else:
						sys.stderr.write('1231 not in all_children_negative' + '\n')

					sys.stderr.write('all_children_positive_map[1231]=' + str(all_children_positive_map[1231]) + '\n')
					'''

				genallevents(data, mastercmds.index(mp), masterpid_name, the_masterpid_pid_positive, all_children_positive_map, f, combine, block)

	else:

		genallevents(data, 0, 'ALL', 0, [], f, combine, block)


	print('{}]}', file = f)


def gentstamps(path):

	tstamps_html = '''

		<html>
		<head>
		<title>Home Page</title>
		</head>
		<body>
		<div style="width:3001px;height:80001px;background-color: Aquamarine">
		<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
		<style>
		.small { font: 10px sans-serif; fill: grey;}
		.normal { font: 12px sans-serif; }
		.heavy { font: bold 30px sans-serif; }
		#event:hover {
		fill: blue;
		}
		</style>

		<defs>

		<pattern id="smallGrid" width="3" height="3" patternUnits="userSpaceOnUse">
		<path d="M 0 0 L 0 3" stroke="gray" stroke-width="0.2"/>
		</pattern>

		<pattern id="grid" width="30" height="10" patternUnits="userSpaceOnUse">
		<rect width="30" height="20" fill="url(#smallGrid)"/>
		<path d="M 0 0 L 0 10" fill="" stroke="gray" stroke-width="1"/>
		</pattern>

		<marker id="startarrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
		<polygon points="10 0, 10 7, 0 3.5" fill="red"/>
		</marker>

		<marker id="endarrow" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto" markerUnits="strokeWidth">
		<polygon points="0 0, 10 3.5, 0 7" fill="red"/>
		</marker>

		<marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5">
		<circle cx="5" cy="5" r="5" fill="red"/>
		</marker>

		<linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
		<stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
		<stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
		</linearGradient>

		</defs>

		<rect x=180 y=20 width="100%" height="100%" fill="url(#grid)" />

		@gridmarkers
		@events

		</svg>
		</div>
		</body>
		</html>

	'''



	tasks = []

	'''
	tasks.append("gw_prov_utopia")

	tasks.append("/bin/sh /etc/utopia/utopia_init.sh")
	tasks.append("execute_dir /etc/utopia/registration.d")
	tasks.append("/etc/utopia/registration.d/25_crond")


	tasks.append("/bin/sh /etc/utopia/service.d/service_cosa.sh cosa-start")
	tasks.append("/usr/bin/CcspCrSsp -subsys eRT.")
	tasks.append("/usr/bin/PsmSsp -subsys eRT.")
	tasks.append("/usr/bin/notify_comp -subsys eRT.")
	tasks.append("/usr/bin/CcspCMAgentSsp -subsys eRT.")
	tasks.append("/usr/bin/CcspPandMSsp -subsys eRT.")


	tasks.append("/bin/sh /usr/ccsp/cosa_start_rem.sh")
	tasks.append("/usr/bin/CcspMtaAgentSsp -subsys eRT.")
	tasks.append("/usr/bin/CcspMoCA -subsys eRT.")
	tasks.append("/usr/bin/CcspTr069PaSsp -subsys eRT.")
	tasks.append("/usr/bin/CcspTandDSsp -subsys eRT.")
	tasks.append("/usr/bin/CcspEthAgent -subsys eRT.")
	tasks.append("/usr/bin/CcspLMLite -subsys eRT.")
	tasks.append("/bin/sh /rdklogger/rdkbLogMonitor.sh")
	tasks.append("/bin/sh /rdklogger/fileUploadRandom.sh")


	tasks.append("/usr/bin/syseventd_fork_helper 12")

	'''

	tasks.append("service_dhcp")

	utopia_services = []

	utopia_services.append('client-notify.sh')
	utopia_services.append('dibbler-client')
	utopia_services.append('dibbler-client')
	utopia_services.append('dibbler-init.sh')
	utopia_services.append('dibbler-server')
	utopia_services.append('dns_sync.sh')
	utopia_services.append('dns_sync.sh')
	utopia_services.append('dnsmasq')
	utopia_services.append('dnsmasq_dhcp.script')
	utopia_services.append('firewall')
	utopia_services.append('firewall_log_handle.sh')
	utopia_services.append('gw_lan_refresh')
	utopia_services.append('handle_sw.sh')
	utopia_services.append('handlesnmpv3.sh')
	utopia_services.append('IGD')
	utopia_services.append('igmpproxy')
	utopia_services.append('ipc_plugin_app')
	utopia_services.append('misc_handler.sh')
	utopia_services.append('mldproxy')
	utopia_services.append('nat_passthrough.sh')
	utopia_services.append('network_response.sh')
	utopia_services.append('nfq_handler')
	utopia_services.append('port_bridging.sh')
	utopia_services.append('postwanstatusevent.sh')
	utopia_services.append('prepare_dhcpv6_config.sh')
	utopia_services.append('relay_control')
	utopia_services.append('service_ccsphs.sh')
	utopia_services.append('service_cosa.sh')
	utopia_services.append('service_crond.sh')
	utopia_services.append('service_dhcp')
	utopia_services.append('service_dhcp_server.sh')
	utopia_services.append('service_dhcpv6_client.sh')
	utopia_services.append('service_dslite')
	utopia_services.append('service_dslite')
	utopia_services.append('service_igd.sh')
	utopia_services.append('service_ipv6')
	utopia_services.append('service_ipv6.sh')
	utopia_services.append('service_mcastproxy.sh')
	utopia_services.append('service_misc.sh')
	utopia_services.append('service_mldproxy.sh')
	utopia_services.append('service_multinet_exec')
	utopia_services.append('service_potd.sh')
	utopia_services.append('service_radiusrelay.sh')
	utopia_services.append('service_routed')
	utopia_services.append('service_routed.sh')
	utopia_services.append('service_wan')
	utopia_services.append('service_wan.sh')
	utopia_services.append('set_ipv6_dns.sh')
	utopia_services.append('ti_dhcp6c')
	utopia_services.append('ti_udhcpc')
	utopia_services.append('udhcpc')
	utopia_services.append('udhcpc.script')
	utopia_services.append('wan_ssh.sh')
	utopia_services.append('zebra')



	results = {}

	for f in (glob.glob(path, recursive = True)):

		#print(f)

		data = log2data(f)


		'''
		r = []
		for task in tasks:
			for key in data:
				if 'cmd' in data[key] and 'exec_ts' in data[key]:

					if data[key]['cmd'].startswith(task):

						start_ts = data[key]['exec_ts']

						end_ts = 0

						if 'exit_ts' in data[key]:
							end_ts = data[key]['exit_ts']

						r.append([data[key]['cmd'], start_ts, end_ts])
		'''


		r = {}

		for key in data:
			if 'cmd' in data[key] and 'exec_ts' in data[key]:

				for item in utopia_services:
					if item + ' ' in data[key]['cmd'] and not any(item in data[key]['cmd'] for item in ['cp ', 'ls ', 'sed ']):

						if item not in r:
							r[item] = []

						start_ts = data[key]['exec_ts']
						end_ts = 0 if 'exit_ts' not in data[key] else data[key]['exit_ts']

						r[item].append([data[key]['cmd'], int(float(start_ts)), int(float(end_ts))])

		results[f] = r


	'''
	for file in results:
		print(file)
		for result in results[file]:
			print(result, '=', results[file][result])
			for occurrence in results[file][result]:
				print(occurrence[0])
	'''

	'''
	for task in tasks:
		l = []
		for key in results:
			for res in results[key]:
				if res[0] == task:
					l.append(str(int(float(res[1]))) + ':' +  str(int(float(res[2]))))
		print(task.ljust(80) + ','.join(l))
	'''


	for line in tstamps_html.splitlines():
		line = line.lstrip()
		if line:
			if line.startswith('@gridmarkers'):
				x = 180
				y = 10 + 5
				for n in range(80):
					print('<text x="%d" y="%d" class="small">%d</text>' %(x, y, n * 10))
					x+= 30

			elif line.startswith('@events'):

				for file in results:

					y = 30
					y1 = 20

					for service in results[file]:

						print('<text x="%d" y="%d" class="normal">%s</text>' %(20, y, service))

						for occurrence in results[file][service]:

							x1 = 200 + occurrence[1] * 3
							x2 = 200 + occurrence[2] * 3

							w = x2 - x1
							if w < 1:
								w = 1

							print('<rect id="event" x="%d" y="%d" width="%d" height="%d" rx="%d" fill="url(#grad1)" stroke="gray" />' %(x1, y1, w, 10, 2))

							#x = 200 + occurrence[2] * 3 + 10
							#print('<text x="%d" y="%d" class="normal">%s</text>' %(x, y, occurrence[0]))

						y+= 10
						y1+= 10



			else :
				print(line)


def makecmdpicklist(data):

	l1 = []
	l1.append("cp")
	l1.append("ls")
	l1.append("ln")
	l1.append("df")
	l1.append("rm")
	l1.append("mv")
	l1.append("head")
	l1.append("mount")
	l1.append("touch")
	l1.append("mkdir")
	l1.append("mknod")
	l1.append("insmod")
	l1.append("killall")
	l1.append("sleep")
	l1.append("tftp")
	l1.append("sed")
	l1.append("awk")
	l1.append("basename")
	l1.append("busybox")
	l1.append("chmod")
	l1.append("cat")
	l1.append("tar")
	l1.append("expr")
	l1.append("find")
	l1.append("grep")
	l1.append("cut")
	l1.append("date")
	l1.append("echo")
	l1.append("pidof")
	l1.append("ps")

	l1.append("ip")
	l1.append("ifconfig")
	l1.append("vconfig")
	l1.append("brctl")
	l1.append("ping")
	l1.append("ping6")

	l1.append("ebtables")
	l1.append("iptables")
	l1.append("ip6tables")
	l1.append("iptables-save")
	l1.append("ip6tables-save")
	l1.append("iptables-restore")
	l1.append("ip6tables-restore")

	l1.append("run-parts")

	l1.append("/sbin/resolvconf")

	l1.append("/usr/sbin/getenv")
	l1.append("getenv")

	l1.append("/usr/sbin/downstream_manager")
	l1.append("/usr/sbin/upstream_manager")
	l1.append("nvread")

	l1.append("print_uptime")

	l1.append("ti_tftp")
	l1.append("ti_todc")

	l1.append("dmcli")
	l1.append("psmcli")

	l1.append("syscfg")
	l1.append("sysevent")
	l1.append("rpcclient")

	#l1.append("execute_dir")

	l1.append("/usr/bin/logger")
	l1.append("/usr/bin/GenFWLog")

	l1.append("utctx_cmd")
	l1.append("swctl")

	l1.append("/etc/udhcpc.script")
	l1.append("/etc/dibbler/client-notify.sh")
	l1.append("/etc/resolvconf/update.d/libc")

	l1.append("/etc/utopia/nat_passthrough.sh")
	l1.append("/etc/utopia/service.d/firewall_log_handle.sh")
	l1.append("/etc/utopia/service.d/misc_handler.sh")
	l1.append("/etc/utopia/service.d/pmon.sh")
	l1.append("/etc/utopia/service.d/service_ccsphs.sh")
	l1.append("/etc/utopia/service.d/service_cosa.sh")
	l1.append("/etc/utopia/service.d/service_crond.sh")
	l1.append("/etc/utopia/service.d/service_dhcp_server.sh")
	l1.append("/etc/utopia/service.d/service_dhcp_server/dnsmasq_dhcp.script")
	l1.append("/etc/utopia/service.d/service_dhcpv6_client.sh")
	l1.append("/etc/utopia/service.d/service_igd.sh")
	l1.append("/etc/utopia/service.d/service_ipv4.sh")
	l1.append("/etc/utopia/service.d/service_ipv6.sh")
	l1.append("/etc/utopia/service.d/service_mcastproxy.sh")
	l1.append("/etc/utopia/service.d/service_misc.sh")
	l1.append("/etc/utopia/service.d/service_mldproxy.sh")
	l1.append("/etc/utopia/service.d/service_multinet/handle_sw.sh")
	l1.append("/etc/utopia/service.d/service_potd.sh")
	l1.append("/etc/utopia/service.d/service_radiusrelay.sh")
	l1.append("/etc/utopia/service.d/service_routed.sh")
	l1.append("/etc/utopia/service.d/service_wan.sh")
	l1.append("/etc/utopia/service.d/service_wan/dns_sync.sh")
	l1.append("/etc/utopia/service.d/set_ipv6_dns.sh")

	l1.append("service_dhcp")
	l1.append("service_dslite")
	l1.append("service_ipv4")
	l1.append("service_ipv6")
	l1.append("service_multinet_exec")
	l1.append("service_routed")
	l1.append("service_wan")



	#atom
	l1.append("tail")
	l1.append("tr")
	l1.append("wc")
	l1.append("chown")
	l1.append("egrep")
	l1.append("pgrep")
	l1.append("seq")
	l1.append("test")
	l1.append("md5sum")
	l1.append("readlink")
	l1.append("/bin/init_man")
	l1.append("/bin/mknod")
	l1.append("cfg")
	l1.append("iwpriv")
	l1.append("iwconfig")
	l1.append("iwlist")
	l1.append("iwgetid")
	l1.append("iwscan")

	l1.append("/bin/touch")
	l1.append("/bin/sleep")
	l1.append("/sbin/ip")
	l1.append("/usr/bin/rpcclient")
	l1.append("/usr/sbin/deviceinfo.sh")

	l1.append("/etc/Wireless/CL2330/sticky_hostapd.sh")
	l1.append("/etc/Wireless/CL2330/hostapd")
	l1.append("/etc/Wireless/CL2330/hostapd_cli")

	l1.append("/etc/Wireless/CL2330/nvram_set cl2330")
	l1.append("/etc/Wireless/CL2330/nvram_get cl2330")

	l1.append("/etc/Wireless/CL242/nvram_set rtdev")
	l1.append("/etc/Wireless/CL242/nvram_get rtdev")
	l1.append("/etc/Wireless/CL242/nvram_set vlan")
	l1.append("/etc/Wireless/CL242/nvram_get vlan")


	l1.append("/bin/sh /etc/Wireless/CBN_CelenoWiFi_24G.sh")
	l1.append("/bin/sh /etc/Wireless/CBN_CelenoWiFi_5G.sh")
	l1.append("/bin/sh /etc/Wireless/CBN_DatFileMonitor_24G.sh")
	l1.append("/bin/sh /etc/Wireless/CBN_DatFileMonitor_5G.sh")
	l1.append("/bin/sh /etc/Wireless/CBN_SetCelenoFromCfg_24G.sh")
	l1.append("/bin/sh /etc/Wireless/CBN_SetCelenoFromCfg_5G.sh")
	l1.append("/bin/sh /etc/Wireless/CL2330/ce_host.sh")
	l1.append("/bin/sh /etc/Wireless/CL242/ce_host.sh")

	l1.append("/usr/sbin/ovsdb-server")
	l1.append("start-stop-daemon")


	l2 = []
	for l in l1:
		l2.append("sh " + l)
		l2.append("/bin/sh " + l)
		l2.append("/bin/bash " + l)
		l2.append("sh -c " + l)

	lf = l1 + l2
	for l in lf:
		lf[lf.index(l)] += ' '


	cmdlist = []
	for key in data:
		if 'cmd' in data[key]:
			cmdlist.append(data[key]['cmd'])

	cmdpicklist = []
	for item in sorted(set(cmdlist)):

		if item.startswith('['):
			pass

		elif item.startswith(tuple(lf)):
			for l in lf:
				if item.startswith(l):
					cmdpicklist.append(l[:-1])
					break

		else:
			cmdpicklist.append(item)

	return sorted(set(cmdpicklist))


def makeoptions(cmdpicklist):

	misc = {}

	l = []
	l.append('print_uptime')
	l.append('/usr/bin/rpcserver')
	l.append('/usr/bin/rpcclient')
	l.append('dmcli')
	l.append('psmcli')
	l.append('syscfg')
	l.append('sysevent')
	misc['Miscellaneous'] = l

	arm = {}

	l = []
	l.append('gw_prov_utopia')
	l.append('/etc/utopia/utopia_init.sh')
	l.append('/etc/start_lighttpd.sh')
	l.append('execute_dir /etc/utopia/registration.d')
	l.append('/etc/utopia/registration.d/25_crond')
	arm['gw_prov_utopia'] = l

	l = []
	l.append('/etc/utopia/service.d/service_cosa.sh')
	l.append('/usr/bin/CcspCrSsp')
	l.append('/usr/bin/PsmSsp')
	l.append('/usr/bin/notify_comp')
	l.append('/usr/bin/CcspCMAgentSsp')
	l.append('/usr/bin/CcspPandMSsp')
	arm['CCSP Cosa'] = l

	l = []
	l.append('/usr/ccsp/cosa_start_rem.sh')
	l.append('/usr/bin/CcspMtaAgentSsp')
	l.append('/usr/bin/CcspMoCA')
	l.append('/usr/bin/CcspTr069PaSsp')
	l.append('/usr/bin/CcspTandDSsp')
	l.append('/usr/bin/CcspEthAgent')
	l.append('/usr/bin/CcspLMLite')
	l.append('/rdklogger/rdkbLogMonitor.sh')
	l.append('/rdklogger/fileUploadRandom.sh')
	arm['CCSP Cosa Rem'] = l

	l = []
	l.append('syseventd')

	l.append('service_dhcp')
	l.append('service_dslite')
	l.append('service_ipv6')
	l.append('service_multinet_exec')
	l.append('service_routed')
	l.append('service_wan')

	l.append('/etc/utopia/service.d/firewall_log_handle.sh')
	l.append('/etc/utopia/service.d/set_ipv6_dns.sh')
	l.append('/etc/utopia/service.d/pmon.sh')

	l.append('/etc/utopia/service.d/service_ccsphs.sh')
	l.append('/etc/utopia/service.d/service_cosa.sh')
	l.append('/etc/utopia/service.d/service_crond.sh')
	l.append('/etc/utopia/service.d/service_dhcp_server.sh')
	l.append('/etc/utopia/service.d/service_dhcp_server/dnsmasq_dhcp.script')
	l.append('/etc/utopia/service.d/service_dhcpv6_client.sh')
	l.append('/etc/utopia/service.d/service_igd.sh')
	l.append('/etc/utopia/service.d/service_ipv6.sh')
	l.append('/etc/utopia/service.d/service_mcastproxy.sh')
	l.append('/etc/utopia/service.d/service_misc.sh')
	l.append('/etc/utopia/service.d/service_mldproxy.sh')
	l.append('/etc/utopia/service.d/service_multinet/handle_gre.sh')
	l.append('/etc/utopia/service.d/service_multinet/handle_sw.sh')
	l.append('/etc/utopia/service.d/service_multinet_exec')
	l.append('/etc/utopia/service.d/service_potd.sh')
	l.append('/etc/utopia/service.d/service_radiusrelay.sh')
	l.append('/etc/utopia/service.d/service_routed.sh')
	l.append('/etc/utopia/service.d/service_wan.sh')
	l.append('/etc/utopia/service.d/service_wan/dns_sync.sh')


	l.append('/etc/utopia/post.d//10_firewall')
	l.append('/etc/utopia/post.d//10_mcastproxy')
	l.append('/etc/utopia/post.d//10_mldproxy')
	l.append('/etc/utopia/post.d//15_igd')

	l.append('/etc/udhcpc.script')
	l.append('/etc/dibbler/client-notify.sh')


	arm['Utopia Services'] = l


	l = []
	l.append('/usr/ccsp/tad/self_heal_connectivity_test.sh')
	l.append('/usr/ccsp/tad/resource_monitor.sh')
	l.append('/usr/ccsp/tad//task_health_monitor.sh')
	l.append('/usr/ccsp/tad/selfheal_aggressive.sh')

	l.append('/usr/ccsp/tad/log_buddyinfo.sh')

	l.append('/usr/ccsp/tad/selfheal_bootup.sh')
	l.append('/usr/ccsp/tad/selfheal_cosa_start_rem.sh')

	l.append('/usr/ccsp/tad/log_hourly.sh')
	l.append('/usr/ccsp/tad/log_mem_cpu_info.sh')

	l.append('/usr/ccsp/tad/uptime.sh')

	l.append('/usr/ccsp/tad/start_gw_heath.sh')
	l.append('/usr/ccsp/tad/check_gw_health.sh')

	l.append('/usr/ccsp/tad/log_sixhourly.sh')

	l.append('/usr/ccsp/tad/syscfg_cleanup.sh')
	l.append('/usr/ccsp/tad/syscfg_recover.sh')

	l.append('/usr/ccsp/tad/getSsidNames.sh')

	l.append('/usr/ccsp/tad/FileHandle_Monitor.sh')

	l.append('/usr/ccsp/tad/remove_max_cpu_usage_file.sh')

	l.append('/usr/ccsp/tad/rxtx_lan.sh')
	l.append('/usr/ccsp/tad/rxtx_cur.sh')

	l.append('/usr/ccsp/tad/check_memory_health.sh')
	l.append('/usr/ccsp/tad/schd_dhcp_server_detection_test.sh')

	l.append('/usr/ccsp/tad/rxtx_sta.sh')
	l.append('/usr/ccsp/tad/rxtx_res.sh')

	l.append('/usr/ccsp/tad/speedtest.sh')

	l.append('/usr/ccsp/tad/corrective_action.sh')
	l.append('/usr/ccsp/tad/cpumemfrag_cron.sh')
	l.append('/usr/ccsp/tad/dhcp_rouge_server_detection.sh')
	l.append('/usr/ccsp/tad/monitor_zombies.sh')
	l.append('/usr/ccsp/tad/oemhooks.sh')
	l.append('/usr/ccsp/tad/selfheal_reset_counts.sh')

	arm['Test and Diagnostics'] = l



	# atom - common

	atom = {}

	l = []
	l.append('/etc/rc3.d/wifi')
	l.append('./cosa_start.sh')
	l.append('/usr/bin/CcspWifiSsp')
	l.append('/usr/bin/meshAgent')
	l.append('/rdklogger/atom_log_monitor.sh')
	l.append('/usr/ccsp/wifi/process_monitor_atom.sh')
	l.append('/usr/bin/wps_btn_monitor')
	atom['Wifi'] = l

	l = []
	l.append('apup_restart.sh')
	l.append('/bin/sh /usr/sbin/CBN_kill_apup')
	l.append('/bin/sh /usr/sbin/apup')
	l.append('/bin/sh /etc/Wireless/CBN_SetCelenoFromCfg_24G.sh')
	l.append('/bin/sh /etc/Wireless/CBN_SetCelenoFromCfg_5G.sh')
	l.append('/bin/sh /etc/Wireless/CBN_CelenoWiFi_24G.sh start')
	l.append('/bin/sh /etc/Wireless/CBN_CelenoWiFi_5G.sh start')
	l.append('/bin/sh /etc/Wireless/CL242/ce_host.sh stop')
	l.append('/bin/sh /etc/Wireless/CL2330/ce_host.sh stop')
	l.append('/bin/sh /etc/Wireless/CL242/ce_host.sh start')
	l.append('/bin/sh /etc/Wireless/CL2330/ce_host.sh start')
	l.append('/bin/sh /etc/Wireless/CBN_DatFileMonitor_24G.sh')
	l.append('/bin/sh /etc/Wireless/CBN_DatFileMonitor_5G.sh')
	l.append('/bin/sh /etc/Wireless/CBN_CelenoWiFi_24G.sh restore_default')
	l.append('/bin/sh /etc/Wireless/CBN_CelenoWiFi_5G.sh restore_default')
	l.append('bandsteering_capabletable')
	atom['Celeno'] = l

	l = []
	l.append('/bin/sh /etc/plume_init.sh')
	l.append('/usr/plume/bin/dm')
	l.append('/usr/plume/bin/wm')
	atom['Plume'] = l


	l = []
	l.append('/bin/sh /etc/init.d/samknows_ispmon')
	atom['SK'] = l



	options = []

	options.append('<option value=\"' + 'None' + '\">' + 'None' + '</option>')
	options.append('<option value=\"' + 'All' + '\">' + 'All' + '</option>')

	for key in misc:
		grouplabel = False
		for item in misc[key]:
			for cmd in cmdpicklist:
				if match(item, cmd):
					if not grouplabel:
						options.append('<optgroup label=\"%s\">' %(key))
						grouplabel = True

					options.append('<option value=\"' + item + '\">' + item + '</option>')
					break
		if grouplabel:
			options.append("</optgroup>")

	for key in arm:
		grouplabel = False
		for item in arm[key]:
			for cmd in cmdpicklist:
				if match(item, cmd):
					if not grouplabel:
						options.append('<optgroup label=\"%s\">' %(key))
						grouplabel = True

					options.append('<option value=\"' + item + '\">' + item + '</option>')
					break
		if grouplabel:
			options.append("</optgroup>")

	for key in atom:
		grouplabel = False
		for item in atom[key]:
			for cmd in cmdpicklist:
				if match(item, cmd):
					if not grouplabel:
						options.append('<optgroup label=\"%s\">' %(key))
						grouplabel = True

					options.append('<option value=\"' + item + '\">' + item + '</option>')
					break
		if grouplabel:
			options.append("</optgroup>")

	return options


def writecgi(cgifile, data, querystring, logfilestash):

	forkstat_cgi = '''
	<form action="" method="get">

	<select id="logfile" name="logfile" style="width:215px" >
	@options_logfile
	</select>

	<select id="cmd" name="cmd" style="width:200px">
	@options_cmd
	</select>

	@text_custom

	@text_block

	@checkbox_busybox
	@checkbox_net
	@checkbox_iw
	@checkbox_cfg
	@checkbox_syscfg
	@checkbox_sysevent
	@checkbox_dmcli
	@checkbox_psmcli
	@checkbox_rpcclient
	@checkbox_expand

	<input type="submit" value="Submit">

	</form>
	@iframe
	'''

	if not querystring:
		querystring = ''

	selected_logfile = fromquerystring(querystring, 'logfile')
	selected_cmd = fromquerystring(querystring, 'cmd')
	text_custom = fromquerystring(querystring, 'custom')
	text_block = fromquerystring(querystring, 'block')

	sys.stderr.write('selected_logfile=' + selected_logfile + '\n')
	sys.stderr.write('selected_cmd=' + selected_cmd + '\n')
	sys.stderr.write('text_custom=' + text_custom + '\n')
	sys.stderr.write('text_block=' + text_block + '\n')

	logfiles = sorted((glob.glob(os.path.join(logfilestash, '*.log'))), key = os.path.basename)

	with open(cgifile.split(',')[0], 'w') as out_file:

		for line in forkstat_cgi.splitlines():
			line = line.lstrip()
			if line:
				if line.startswith('@options_logfile'):
					for f in logfiles:
						f = os.path.basename(f)
						s = ''
						if f == selected_logfile:
							s = ' selected'
						out_file.write('<option value="%s"%s>%s</option>'%(f, s, f) + '\n')

				elif line.startswith('@checkbox_'):
					name = line.split('_')[1]
					s = ''
					if fromquerystring(querystring, name) == 'yes':
						s = ' checked'
					out_file.write('<input type="checkbox" name="%s" value="yes"%s>'%(name, s) + '\n')
					out_file.write('<label for="%s">%s</label>'%(name, name) + '\n')

				elif line.startswith('@options_cmd'):
					if not data:
						data = log2data(logfiles[0])

					selected = False
					for option in makeoptions(makecmdpicklist(data)):

						if selected_cmd and ('\"' + selected_cmd + '\"' in option or selected_cmd + ' ' in option):
							out_file.write(option.replace('>' + selected_cmd, ' selected>' + selected_cmd) + '\n')
							selected = True
						else:
							out_file.write(option + '\n')

					if selected_cmd and not selected:
						out_file.write('<option value=\"' + selected_cmd + '\" selected>' + selected_cmd + '</option>\n')

				elif line.startswith('@text_custom'):

					out_file.write('<input type="text" id="custom" style="width:200px" name="custom" value="%s">\n'%(text_custom))

				elif line.startswith('@text_block'):

					out_file.write('<input type="text" id="block" style="width:200px" name="block" value="%s">\n'%(text_block))

				elif line.startswith('@iframe'):
					if (selected_cmd and selected_cmd != 'None') or text_custom != '':
						out_file.write('<iframe id="serviceFrameSend" src="./forkstat-iframe.cgi?' + querystring + '" width="100%" height="100%" frameborder="0">' + '\n')
					else:
						for line in landing_html.splitlines():
							line = line.lstrip()
							if line:
								out_file.write(line + '\n')

				else:
					out_file.write(line + '\n')


def writecgi_file(cgi_file):

	forkstat_cgi_file = '''
	#!/bin/bash
	#set -x
	#set -e
	forkstat=/home/rev/git/redkite/notes/rdk-b/python3/forkstat.py
	echo 'Content-type: text/html'
	echo ''
	$forkstat -s /home/rev/cgi-bin -q "$QUERY_STRING" 2> /dev/null -i /dev/stdout | cat
	'''

	with open(cgi_file, 'w') as out_file:
		for line in forkstat_cgi_file.splitlines():
			line = line.lstrip()
			if line:
				out_file.write(line + '\n')


def writecgi_iframe_file(cgi_iframe_file):

	forkstat_cgi_iframe_file = '''
	#!/bin/bash
	#set -x
	#set -e
	forkstat=/home/rev/git/redkite/notes/rdk-b/python3/forkstat.py
	trace2html=/home/rev/git/catapult/tracing/bin/trace2html
	echo 'Content-type: text/html'
	echo ''
	if [ ! -z $QUERY_STRING ]; then
	title=`python3 -c "import sys, urllib.parse as ul; print(ul.unquote(ul.unquote(sys.argv[1])))" "$QUERY_STRING"`
	$forkstat -s /home/rev/cgi-bin -q "$QUERY_STRING" 2> /dev/null | $trace2html --quiet --title "Trace for $title" /dev/stdin --output /dev/stdout | cat
	else
	echo 'No Data..'
	fi
	'''

	with open(cgi_iframe_file, 'w') as out_file:
		for line in forkstat_cgi_iframe_file.splitlines():
			line = line.lstrip()
			if line:
				out_file.write(line + '\n')

#@profile
def main():

	usage = "usage: %prog <forkstat.log | forkstat.json> [options]"

	parser = OptionParser(usage = usage, description = None)

	parser.add_option("-o", dest = "outfile",
					action = "store", type = "string",
					help = "use output file instead of stdout")

	parser.add_option("-c", dest = "nocombine",
					action = "store_false", default=True,
					help = "no combining cmd parts i.e. expand")

	parser.add_option("-x", dest = "noeventoutput",
					action = "store_true", default=False,
					help = "no event output")

	parser.add_option("-d", dest = "dumpjson",
					action = "store", type = "string",
					help = "write raw json from the log file to specified file")

	parser.add_option("-l", dest = "cmdlist",
					action = "store", type = "string",
					help = "write cmdlist to specified file")

	parser.add_option("-p", dest = "cmdpicklist",
					action = "store", type = "string",
					help = "write cmdpicklist to specified file")

	parser.add_option("-i", dest = "cgi",
					action = "store", type = "string",
					help = "write html form")

	parser.add_option("-f", dest = "cgi_file",
					action = "store", type = "string",
					help = "write <>.cgi file")

	parser.add_option("-g", dest = "cgi_iframe_file",
					action = "store", type = "string",
					help = "write <>-iframe.cgi file")

	parser.add_option("-t", dest = "tstamps",
					action = "store", type = "string",
					help = "write tstamps to csv")

	parser.add_option("-m", dest = "mastercmds",
					action = "append", type = "string",
					help = "cmdset is a subset of positive / negative descendants e.g. -m mycmds=cmd1,-cmd2 -m mycmds2=cmd4,cmd5")

	parser.add_option("-s", dest = "logfilestash",
					action = "store", type = "string",
					help = "path to logfile stash")

	parser.add_option("-q", dest = "querystring",
					action = "store", type = "string",
					help = "cmdset is a url querystring e.g. logfile=arm.log&cmd=%2Fusr%2Fbin%2FPsmSsp+-subsys+eRT.")


	(options, args) = parser.parse_args()


	if len(sys.argv) == 1:
		parser.print_help()
		exit(0)

	if options.tstamps:
		gentstamps(options.tstamps)
		exit(0)

	data = []

	if options.querystring:

		data = log2data(options.logfilestash + '/' + fromquerystring(options.querystring, 'logfile'))

	else:
		if sys.argv[1].endswith('.log'):
			data = log2data(sys.argv[1])

		elif sys.argv[1].endswith('.json'):
			with open(sys.argv[1]) as json_data:
				data = json.load(json_data)
		else:
			#parser.print_help()
			#exit(0)
			pass


	if options.dumpjson:
		with open(options.dumpjson, 'w') as out_file:
			out_file.write(json.dumps(data, indent = 4))

	if options.cmdlist:
		cmdlist = []
		for key in data:
			if 'cmd' in data[key]:
				cmdlist.append(data[key]['cmd'])
		with open(options.cmdlist, 'w') as out_file:
			out_file.write('\n'.join(sorted(set(cmdlist))) + '\n')

	if options.cmdpicklist:
		with open(options.cmdpicklist, 'w') as out_file:
			out_file.write('\n'.join(makecmdpicklist(data)) + '\n')

	if options.cgi:
		writecgi(options.cgi, data, options.querystring, options.logfilestash)
		exit(0)

	if options.cgi_file:
		writecgi_file(options.cgi_file)

	if options.cgi_iframe_file:
		writecgi_iframe_file(options.cgi_iframe_file)

	if data:

		combine = True
		if options.querystring:
			if fromquerystring(options.querystring, 'expand') == 'yes':
				combine = False
		elif options.nocombine:
			combine = False

		if not options.noeventoutput:

			if options.outfile:
				sys.stdout = open(options.outfile,"w")

			writeresults(data, options, sys.stdout, combine)

if __name__ == '__main__':
	main()
