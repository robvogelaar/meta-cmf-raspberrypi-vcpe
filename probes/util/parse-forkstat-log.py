#!/usr/bin/env python3

import sys, os, json, datetime, glob

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


def is_valid_float(s):
	"""
	Check if the string is a valid float number.
	"""

	try:
		float(s)
		return True
	except ValueError:
		return False


def process_lines_for_corruption(lines):

	corruptlines = []
	i = 0
	while i < len(lines):

		if not is_valid_float(lines[i].split()[0]):
			corruptlines.append(i)
			i+= 1

		elif ' fork ' in lines[i] and ' parent ' in lines[i] and ' fork ' in lines[i + 1] and ' child ' in lines[i + 1]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			if len(lines[i + 1].split(None, 4)) != 5:
				corruptlines.append(i + 1)
			i+= 2

		elif ' exec ' in lines[i]:
			if len(lines[i].split(None, 3)) != 4:
				corruptlines.append(i)
			i+= 1

		elif ' exit ' in lines[i]:
			if len(lines[i].split(None, 2)) != 3:
				corruptlines.append(i)
			i+= 1

		elif ' clone ' in lines[i] and ' parent ' in lines[i] and ' clone ' in lines[i + 1] and ' thread ' in lines[i + 1]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			if len(lines[i + 1].split(None, 4)) != 5:
				corruptlines.append(i + 1)
			i+= 2

		elif ' sid ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			i+= 1

		elif ' uid ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			i+= 1

		elif ' comm ' in lines[i]:
			if len(lines[i].split(None, 3)) != 4:
				corruptlines.append(i)
			i+= 1

		elif ' ptrce ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			i+= 1

		elif ' core ' in lines[i]:
			if len(lines[i].split(None, 4)) != 5:
				corruptlines.append(i)
			i+= 1

		else:

			corruptlines.append(i)
			i+= 1

	return corruptlines


def log2data(infile):

	lines = []
	with open(infile, 'r', encoding = 'ascii', errors = 'ignore') as fp:
		lines = fp.readlines()

	if not lines:
		sys.stderr.write('empty file \"%s\" \n' %(infile))
		return []


	#sys.stderr.write('parsing \"%s\" %d lines..\n' %(infile, len(lines)))

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



	# check for corrupt lines
	corruptlines = process_lines_for_corruption(lines)
	if corruptlines:
		for l in corruptlines:
			sys.stderr.write('corruptline: [' + lines[l][:-1] + ']\n')

		lines = [item for idx, item in enumerate(lines) if idx not in corruptlines]
		#sys.stderr.write('exiting\n')
		#exit(1)



	# check for time jumps
	prev_time = 0.0
	for line in lines:
		#print(line[:-1])
		time = float(line.split()[0])
		if prev_time == 0:
			prev_time = time
		if abs(time - prev_time) > 3600:
			sys.stderr.write('jump detected: ' + line +'\nexiting\n')
			exit(1)
		prev_time = time


	#with open('./lines.txt', 'w') as out_file:
	#	for line in lines:
	#		out_file.write(line)


	print("#lines=", len(lines))

	ppid1_cmds = []
	data = {}
	i = 0
	while i < len(lines):

		#print(lines[i][:-1])

		items = lines[i].split()
		items1 = '' if (i + 1) == len(lines) else lines[i + 1].split()

		#fork parent
		#fork child
		#-> new pid

		if items[1] == 'fork' and items[3] == 'parent' and items1[1] == 'fork' and items1[3] == 'child' :
			ppid = int(items[2])
			pid = int(items1[2])

			data[pid] = {}
			#data[pid]['nr_forks'] = 0
			#data[pid]['nr_execs'] = 0
			#data[pid]['execs'] = []
			#data[pid]['nr_threads'] = 0
			data[pid]['fork_ts'] = str(float(items1[0]))
			data[pid]['parent_pid'] = ppid
			data[pid]['parent_cmd'] = ' '.join(items[4:])
			data[pid]['cmd'] = ' '.join(items1[4:])

			#if ppid in data:
			#	data[ppid]['nr_forks']+= 1


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
						sys.stderr.write(lines[i][:-1] + '\n')
						sys.stderr.write(lines[i + 1][:-1] + '\n')
						sys.stderr.write('previous matching pid not found, internal error, not exiting\n')
						#exit(1)
						pass

			i+= 2


		elif items[1] == 'exec':
			pid = int(items[2])

			if pid in data:
				data[pid]['exec_ts'] = str(float(items[0]))
				data[pid]['cmd'] = ' '.join(items[3:])
				#data[pid]['nr_execs']+= 1
				#data[pid]['execs'].append(' '.join(items[3:]))

			else:
				#sys.stderr.write('exec with no pid in data\n')
				pass
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
			#data[pid]['nr_forks'] = 0
			#data[pid]['nr_execs'] = 0
			#data[pid]['execs'] = []
			#data[pid]['nr_threads'] = 0
			data[pid]['clone_ts'] = str(float(items1[0]))
			data[pid]['parent_pid'] = ppid
			data[pid]['parent_cmd'] = ' '.join(items[4:])
			data[pid]['cmd'] = ' '.join(items1[4:])

			#if ppid in data:
			#	data[ppid]['nr_threads']+= 1

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
			i+= 1
			sys.stderr.write(lines[i][:-1] + '\n')
			sys.stderr.write('unparsed line, internal error, exiting\n')
			exit(1)


	sys.stderr.write('%d processes with parent pid 1:\n' %(len(ppid1_cmds)))
	sys.stderr.write('%s, %d processes with parent pid 1:\n' %(infile, len(ppid1_cmds)))
	for count, ppid1_cmd in enumerate(sorted(ppid1_cmds)):
		sys.stderr.write('%2d \"%s\"\n'%(count, ppid1_cmd))


	#for key in data:
	#	if data[key]['cmd'] == '/sbin/init':
	#		sys.stderr.write('/sbin/init/\n')
	#		break


	#found_ts = False
	#for key in data:
	#	for ts in ['exec_ts', 'fork_ts', 'clone_ts', 'exit_ts', 'sid_ts', 'uid_ts']:
	#		if ts in data[key]:
	#			start = data[key][ts]
	#			sys.stderr.write('start=%s\n'%(start))
	#			found_ts = True
	#			break
	#	if found_ts:
	#		break

	#for key in data:
	#	for ts in ['exec_ts', 'fork_ts', 'clone_ts', 'exit_ts', 'sid_ts', 'uid_ts']:
	#		if ts in data[key]:
	#			#data[key][ts] = str(float(data[key][ts]) - float(start))
	#			data[key][ts] = str(float(data[key][ts]))

	return data



def familytree(data, pid):

	tree_pidscmds = []
	parent = pid
	while parent in data:
		#sys.stderr.write('parent=' + str(parent) + '\n')
		tree_pidscmds.append(str(data[parent]['parent_pid']) + ' ' + data[parent]['parent_cmd'])
		parent = data[parent]['parent_pid']

	return tree_pidscmds



def find_descendants(pid, data):
	descendants = []

	# Helper function for recursive search
	def find_children_recursive(current_pid):
		for child_pid in data:
			if data[child_pid].get('parent_pid') == current_pid:
				descendants.append(child_pid)
				find_children_recursive(child_pid)

	find_children_recursive(pid)
	return descendants



def create_wireshark_like_html(exchanges, htmlfilename):
	# HTML structure with CSS and JavaScript
	html_content = """
	<!DOCTYPE html>
	<html>
	<head>
	<style>
		body {
			font-family: 'Consolas', monospace;
			font-size: 9pt;
		}
		.container {
			display: flex;
			flex-direction: column;
			height: 100vh;
		}
		.pane {
			border: 1px solid #ddd;
			margin: 5px;
			padding: 5px;
		}

		.list-pane {
			height: 60%; /* Adjust the height as needed */
			display: flex;
			flex-direction: column;
		}

		.details-pane {
			height: 40%; /* Adjust the height as needed */
			border: 1px solid #ddd;
			margin: 5px;
			padding: 5px;
		}

		#detailsPane {
		  display: flex;
		}

		.content-div {
		  margin-right: 10px; /* Adjust margin as needed for spacing between divs */
		}

		.list-header, .exchange-item {
			display: flex;
			justify-content: flex-start;
			padding: 5px;
		}
		.list-header {
			background-color: #ddd;
		}
		.list-content {
			overflow: auto;
			flex-grow: 1;
		}
		.exchange-item:hover {
			background-color: #cccccc;
			filter: brightness(90%); /* Adjust the brightness value as needed */
		}
		.selected {
			background-color: #b0b0b0;
			filter: brightness(80%); /* Adjust the brightness value as needed */
		}
		.stamp {
			margin: 0 5px;
			min-width: 100px; /* Adjust the width as needed */
		}
		.runtime {
			margin: 0 5px;
			min-width: 100px; /* Adjust the width as needed */
		}

		.thread {
			margin: 0 5px;
			min-width: 50px; /* Adjust width as needed */
			text-align: right;
		}

		.process {
			margin: 0 5px;
			min-width: 800px; /* Adjust width as needed */
		}

	</style>
	</head>
	<body>

	<div class="container">
		<div class="list-pane pane">
			<div class="list-header">
				<span class="stamp" data-sort="stamp">T</span>
				<span class="runtime" data-sort="runtime">Runtime</span>
				<span class="thread" data-sort="thread">Thread</span>
				<span class="process" data-sort="process">Process</span>
			</div>
			<div class="list-content" id="listPane">
				<!-- List of exchanges will be populated here -->
			</div>
		</div>

		<div class="details-pane pane" id="detailsPane">
			<!-- Details of the selected exchange will be shown here -->
			<div id="requestDiv" class="content-div"></div>
			<div id="responseDiv" class="content-div"></div>
		</div>

	</div>

	<script>
	var colorMap = {};

	var currentSortColumn = ""; // Track the currently sorted column
	var isSortAscending = true; // Track the sorting order


	// At the beginning of your script
	var currentSortColumn = null; // Store the current column used for sorting
	var isSortAscending = true; // Store the sorting order


	function sortExchanges(column) {
		// Check if the same column is clicked again and reverse the sorting order
		if (currentSortColumn === column) {
			isSortAscending = !isSortAscending;
		} else {
			// If a different column is clicked, start with ascending order
			isSortAscending = true;
		}
		currentSortColumn = column;

		exchanges.sort(function (a, b) {
			var valueA = a[column];
			var valueB = b[column];

			// Check if values are numeric and parse them as floats for sorting
			if (!isNaN(parseFloat(valueA)) && !isNaN(parseFloat(valueB))) {
				valueA = parseFloat(valueA);
				valueB = parseFloat(valueB);
			}

			if (typeof valueA === "number" && typeof valueB === "number") {
				return isSortAscending ? valueA - valueB : valueB - valueA;
			} else {
				var strValueA = (valueA || "").toString().toLowerCase();
				var strValueB = (valueB || "").toString().toLowerCase();
				return isSortAscending ? strValueA.localeCompare(strValueB) : strValueB.localeCompare(strValueA);
			}
		});

		renderExchanges();
	}


	function renderExchanges() {
		var listPane = document.getElementById("listPane");
		listPane.innerHTML = ""; // Clear existing content
		exchanges.forEach(addExchangeToList); // Re-add sorted exchanges
	}


	function getProcessColor(process) {
		var key = process;
		if (!colorMap[key]) {
			// Generate a random color
			colorMap[key] = 'hsl(' + Math.random() * 360 + ', 70%, 80%)';
		}
		return colorMap[key];
	}

	function findAncestors(exchange, exchanges) {
		var ancestors = [];
		var currentParentPid = exchange.parent_pid;

		ancestors.push("<b>" + exchange.pid + ' ' + exchange.thread + ' ' + exchange.process + "</b>");

		while (currentParentPid) {
			var parentExchange = exchanges.find(function(ex) {
				return ex.pid === currentParentPid;
			});
			if (parentExchange) {
				ancestors.push(parentExchange.pid + ' ' + parentExchange.thread + ' ' + parentExchange.process);
				currentParentPid = parentExchange.parent_pid;
			} else {
				break;
			}
		}
		return ancestors;
	}

	function showDetails(exchange, element) {
		var requestDiv = document.getElementById("requestDiv");
		var responseDiv = document.getElementById("responseDiv");

		requestDiv.innerHTML = "";

		var ancestors = findAncestors(exchange, exchanges);
		if (ancestors.length > 0) {
			var ancestorsList = ancestors.map(function(ancestor) {
				return '<li>' + ancestor + '</li>';
			}).join('');
			responseDiv.innerHTML = "<b>Ancestors:</b><ul>" + ancestorsList + "</ul>";
		} else {
			responseDiv.innerHTML = "<b>Ancestors:</b> None";
		}

		var exchangesItems = document.getElementsByClassName("exchange-item");
		for (var i = 0; i < exchangesItems.length; i++) {
			exchangesItems[i].classList.remove("selected");
		}

		element.classList.add("selected");
	}


	function addExchangeToList(exchange, index) {
		var listPane = document.getElementById("listPane");
		var div = document.createElement("div");
		div.className = "exchange-item";
		div.style.backgroundColor = getProcessColor(exchange.process);

		div.appendChild(createSpan("stamp", exchange.stamp || ""));
		div.appendChild(createSpan("runtime", exchange.runtime || ""));
		div.appendChild(createSpan("thread", exchange.thread || ""));
		div.appendChild(createSpan("process", exchange.process || ""));

		div.onclick = function() { showDetails(exchange, div); };
		listPane.appendChild(div);
	}

	function createSpan(className, text) {
		var span = document.createElement("span");
		span.className = className;
		span.innerHTML = text;
		return span;
	}

	var exchanges = """ + str(exchanges) + """;

	exchanges.forEach(addExchangeToList);

	window.onload = function () {

		var exchanges = """ + str(exchanges) + """;

		sortExchanges("stamp")

		if (exchanges.length > 0) {
			// Select the first exchange item and show its details
			var firstExchangeItem = document.querySelector(".exchange-item");
			showDetails(exchanges[0], firstExchangeItem);
		}

		document.querySelectorAll(".list-header span").forEach(function (header) {
			header.addEventListener("click", function () {
				var sortAttribute = this.getAttribute("data-sort");
				if (sortAttribute) {
					sortExchanges(sortAttribute);
				}
			});
		});
	};


	</script>

	</body>
	</html>
	"""

	# Write the HTML content to a file
	with open(htmlfilename, "w") as file:
		file.write(html_content)
	print(htmlfilename)



#@profile
def main():

	# Ensure the script was called with an argument
	if len(sys.argv) < 2:
		print(f"Usage: {sys.argv[0]} <path_to_log_file>")
		sys.exit(1)

	data = []
	data = log2data(sys.argv[1])

	print('log2data done')

	print(len(data))


	d_init = 0
	d_init2 = 0
	for d in data:
		#if data[d]['cmd'] == '/sbin/init' and data[d]['parent_cmd'].startswith("[lxc monitor]"):
		#if data[d]['cmd'] == '/sbin/init' and "sid_ts" in data[d]:

		#print(data[d]['cmd'])
		if data[d]['cmd'] == '/bin/sh /etc/init.d/rcS':
			print('init found (/etc/init.d/rcS)')
			exit(1)


		# and data[d]['parent_cmd'].startswith("[lxc monitor]"):


		#print(data[d]['cmd'])
		if 'sbin/init' in data[d]['cmd']:
			print('init found (sbin/init) ')
			#exit(1)

			#d_init = d
			d_init = data[d]['parent_pid']
			d_init2 = d
			break

	if d_init == 0:
		print('init not found')
		exit(1)
	else:
		#print('init found: [%s]:(%s)' %(data[d_init2]['cmd'], data[d_init]['parent_cmd']))
		pass

	#exit(1)

	#with open(sys.argv[1] + '.json', 'w') as out_file:
	#	out_file.write(json.dumps(data, indent = 4))

	#print(familytree(data, 128564))

	init_stamp = float(data[d_init]["sid_ts"])

	descendants = find_descendants(d_init , data)

	entries = []
	for d in descendants:
		#print(data[d])

		stamp = data[d]["fork_ts"] if "fork_ts" in data[d] else data[d]["clone_ts"] if "clone_ts" in data[d] else data[d]["fork_ts"]
		stamp = round((float(stamp) - init_stamp),9)

		runtime = 'long-running'
		if "exit_ts" in data[d]:
			runtime = round(float(data[d]["exit_ts"]) - float(data[d]["fork_ts"] if "fork_ts" in data[d] else data[d]["clone_ts"] if "clone_ts" in data[d] else data[d]["fork_ts"]),9)

		thread = "&check;" if "clone_ts" in data[d] else ""

		if (runtime== 0):
			print('runtime = 0')
			print(data[d])

		entries.append({
			"stamp": stamp,
			"runtime": runtime,
			"process": data[d]["cmd"],
			"pid": d,
			"parent_pid": data[d]["parent_pid"],
			"thread": thread,
		})

	create_wireshark_like_html(entries, sys.argv[1].split('.')[0] + '.html')


if __name__ == '__main__':
	main()
