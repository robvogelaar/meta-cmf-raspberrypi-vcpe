#!/usr/bin/env python3

import re
import sys
import msgpack


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
			height: 80%; /* Adjust the height as needed */
			display: flex;
			flex-direction: column;
		}

		.details-pane {
			height: 20%; /* Adjust the height as needed */
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
			min-width: 150px; /* Adjust the width as needed */
		}
		.process {
			margin: 0 5px;
			min-width: 200px; /* Adjust width as needed */
		}
		.cmd {
			margin: 0 5px;
			min-width: 200px; /* Adjust width as needed */
		}
		.name {
			margin: 0 5px;
			min-width: 400px; /* Adjust width as needed */
		}
		.value {
			margin: 0 5px;
			min-width: 400px; /* Adjust width as needed */
		}


	</style>
	</head>
	<body>

	<div class="container">
		<div class="list-pane pane">
			<div class="list-header">
				<span class="stamp" data-sort="stamp">T</span>
				<span class="process" data-sort="process">Process</span>
				<span class="cmd" data-sort="cmd">Cmd</span>
				<span class="name" data-sort="method">Name</span>
				<span class="value" data-sort="param">Value</span>
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


	function sortExchanges1(column) {

		// Check if the same column is clicked again and reverse the sorting order
		if (currentSortColumn === column) {
			isSortAscending = !isSortAscending;
		} else {
			// If a different column is clicked, start with ascending order
			isSortAscending = true;
		}
		currentSortColumn = column;


		// Log the state of exchanges before sorting

		// Sorting logic...
		// [Your sorting logic here]
		exchanges.sort(function (a, b) {
			var valueA = a[column];
			var valueB = b[column];

			// Handle numeric and string comparisons
			if (typeof valueA === "number" && typeof valueB === "number") {
				return isSortAscending ? valueA - valueB : valueB - valueA;
			} else {
				var strValueA = (valueA || "").toString().toLowerCase();
				var strValueB = (valueB || "").toString().toLowerCase();
				return isSortAscending ? strValueA.localeCompare(strValueB) : strValueB.localeCompare(strValueA);
			}
		});

		// Log the state of exchanges after sorting

		// Call function to update the display
		renderExchanges();
	}


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

	// [Rest of your script]


	function getProcessCmdColor(process, cmd) {
		var key = process + '-' + cmd;
		if (!colorMap[key]) {
			// Generate a random color
			colorMap[key] = 'hsl(' + Math.random() * 360 + ', 70%, 80%)';
		}
		return colorMap[key];
	}

	function showDetails(exchange, element) {

		// Create two new div elements for "Request" and "Response"
		var requestDiv = document.getElementById("requestDiv");
		var responseDiv = document.getElementById("responseDiv");

		// Set the innerHTML for "Request" and "Response"
		requestDiv.innerHTML = "<b>Process:</b> " + exchange.cmdline + "(" + exchange.pid  +")";
		responseDiv.innerHTML = "<b>Parent:</b> " + exchange.parentcmdline  + "(" + exchange.ppid  + ")";

		var exchanges = document.getElementsByClassName("exchange-item");
		for (var i = 0; i < exchanges.length; i++) {
			exchanges[i].classList.remove("selected");
		}


		element.classList.add("selected");
	}

	function addExchangeToList(exchange, index) {
		var listPane = document.getElementById("listPane");
		var div = document.createElement("div");
		div.className = "exchange-item";
		div.style.backgroundColor = getProcessCmdColor(exchange.process, exchange.cmd);

		div.appendChild(createSpan("counter", exchange.counter || ""));
		div.appendChild(createSpan("stamp", exchange.stamp || ""));
		div.appendChild(createSpan("process", exchange.process || ""));
		div.appendChild(createSpan("cmd", exchange.cmd || ""));
		div.appendChild(createSpan("name", exchange.name || ""));
		div.appendChild(createSpan("value", exchange.value || ""));

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



# Ensure the script was called with an argument
if len(sys.argv) < 2:
	print(f"Usage: {sys.argv[0]} <path_to_log_file>")
	sys.exit(1)

# Take the log file path from the first argument
log_file_path = sys.argv[1]


syscfgs = []

prev_stamp = None
prev_cmd = ''
with open(log_file_path, 'r') as file:

	for line in file:

		#print(line[:-1])


		# 1674753.423493||CcspCMAgentSsp||898||/sbin/init ||1||/sbin/init ||syscfg_get||bridge_mode||0
		parts = line.split('||')

		syscfg = {}

		if not prev_stamp:
			prev_stamp = float(parts[0])

		syscfg["stamp"] = str(round(float(parts[0]) - prev_stamp, 6))
		syscfg["process"] = parts[1]
		syscfg["pid"] = parts[2]
		syscfg["cmdline"] = parts[3]
		syscfg["ppid"] = parts[4]
		syscfg["parentcmdline"] = parts[5]
		syscfg["cmd"] = parts[6]
		syscfg["name"] = parts[7]
		syscfg["value"] = parts[8]

		# do not populate set_ns if preceded with set_nns
		if syscfg["cmd"] == 'syscfg_set_ns' and prev_cmd == 'syscfg_set_nns':
			pass
		elif syscfg["cmd"] == 'syscfg_set_ns' and prev_cmd == 'syscfg_set_ns_commit':
			pass
		elif syscfg["cmd"] == 'syscfg_set_ns' and prev_cmd == 'syscfg_set_nns_commit':
			pass
		elif syscfg["cmd"] == 'syscfg_set_ns' and prev_cmd == 'syscfg_set_ns_u':
			pass
		elif syscfg["cmd"] == 'syscfg_set_ns_u_commit' and prev_cmd == 'syscfg_set_nns_u_commit':
			pass
		elif syscfg["cmd"] == 'syscfg_set_ns_commit' and prev_cmd == 'syscfg_set_nns_commit':
			pass
		else:
			syscfgs.append(syscfg)
		prev_cmd = syscfg["cmd"]


plain_cfgs = []
for syscfg in syscfgs:

	plain_cfgs.append({
		"stamp": syscfg["stamp"],
		"process": syscfg["process"],
		"pid": syscfg["pid"],
		"cmdline": syscfg["cmdline"],
		"ppid": syscfg["ppid"],
		"parentcmdline": syscfg["parentcmdline"],
		"cmd": syscfg["cmd"],
		"name": syscfg["name"],
		"value": syscfg["value"],
	})


create_wireshark_like_html(syscfgs, sys.argv[1].split('.')[0] + '.html')
