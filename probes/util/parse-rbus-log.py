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
		.counter,.t1,.t2 {
			margin: 0 5px;
			min-width: 40px; /* Adjust the width as needed */
		}
		.source, .destination {
			margin: 0 5px;
			min-width: 150px; /* Adjust width as needed */
		}
		.value {
			margin: 0 5px;
			min-width: 400px; /* Adjust width as needed */
		}

		.remark {
			margin: 0 5px;
			min-width: 150px; /* Adjust width as needed */
			font-style: italic; /* Make the content italic */
			font-size: 7pt;
		}

		.method {
			margin: 0 5px;
			min-width: 150px; /* Adjust the width as needed */
		}
		.param {
			margin: 0 5px;
			min-width: 750px; /* Adjust the width as needed */
		}

	</style>
	</head>
	<body>

	<div class="container">
		<div class="list-pane pane">
			<div class="list-header">
				<span class="counter" data-sort="counter">No.</span>
				<span class="t1" data-sort="t1">T1</span>
				<span class="t2" data-sort="t2">T2</span>
				<span class="source" data-sort="source">Source</span>
				<span class="destination" data-sort="destination">Destination</span>
				<span class="method" data-sort="method">Method</span>
				<span class="param" data-sort="param">Param</span>
				<span class="value" data-sort="value">Value</span>
				<span class="remark" data-sort="remark">remark</span>
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


	function renderExchanges() {
		var listPane = document.getElementById("listPane");
		listPane.innerHTML = ""; // Clear existing content
		exchanges.forEach(addExchangeToList); // Re-add sorted exchanges
	}

	// [Rest of your script]


	function getSourceDestinationColor(source, destination) {
		var key = source + '-' + destination;
		if (!colorMap[key]) {
			// Generate a random color
			colorMap[key] = 'hsl(' + Math.random() * 360 + ', 70%, 80%)';
		}
		return colorMap[key];
	}

	function showDetails(exchange, element) {


		var detailsPane = document.getElementById("detailsPane");

		// Create two new div elements for "Request" and "Response"
		var requestDiv = document.getElementById("requestDiv");
		var responseDiv = document.getElementById("responseDiv");

		// Set the innerHTML for "Request" and "Response"
		requestDiv.innerHTML = "<b>Request:</b> " + exchange.request;
		responseDiv.innerHTML = "<b>Response:</b> " + exchange.response;

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
		div.style.backgroundColor = getSourceDestinationColor(exchange.source, exchange.destination);

		div.appendChild(createSpan("counter", exchange.counter || ""));
		div.appendChild(createSpan("t1", exchange.t1 || ""));
		div.appendChild(createSpan("t2", exchange.t2 || ""));
		div.appendChild(createSpan("source", exchange.source || ""));
		div.appendChild(createSpan("destination", exchange.destination || ""));
		div.appendChild(createSpan("method", exchange.method || ""));
		div.appendChild(createSpan("param", exchange.param || ""));
		div.appendChild(createSpan("value", exchange.value || ""));
		div.appendChild(createSpan("remark", exchange.remark || ""));

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


def unpack_msgpack_response_items(data):
	response_items = []
	#print("data")
	#print(data)
	while data:
		try:
			# Unpack the next item from the data
			item = msgpack.unpackb(data, raw=False)
			response_items.append(item)
			# Serialize the item back to a bytes object to find its length
			packed_item = msgpack.packb(item, use_bin_type=True)
			# Update the data to the remaining part after the current item
			data = data[len(packed_item):]
		except msgpack.ExtraData as e:
			# If there is extra data, add the unpacked data and set the remaining data
			response_items.append(e.unpacked)
			data = e.extra
		except msgpack.UnpackValueError as e:
			# Handle other unpacking errors (e.g., incomplete or corrupted data)
			#print(f"UnpackValueError: {e}")
			#print(response_items)
			break
	#print("response_items")
	#print(response_items)

	return response_items


def parse_buffer(buffer_str):
	#print()
	#print("{" + f"{buffer_str}" + "}")
	# Split the buffer into elements and filter out empty strings
	elements = filter(None, buffer_str.split(' '))
	parsed_response_items = []
	# Prepare a bytes object to store bytes for msgpack
	bytes_obj = b''

	for item in elements:
		# Check if the item is a byte representation, e.g., 0x12
		if item.startswith('0x'):
			# Append the byte to the bytes object
			#print('here:', item)
			bytes_obj += bytes([int(item, 16)])
		else:
			print('unexpected:', item)
			exit()
			# It's a string, append it to the list
			parsed_response_items.append(item.strip('"'))

	#print(bytes_obj)

	unpacked_response_items = unpack_msgpack_response_items(bytes_obj)
	#print(unpacked_response_items)
	return unpacked_response_items



def get_message_content(m):

	#print("m=%s" %m)

	if len(m) == 0:
		return ''

	m_str = '<br>'  # Start with a line break to separate this content from previous content
	
	# Create a list of element names and values
	elements = [
		("No.", m.get('counter', '')),
		("Sender Inbox", m.get('sender_inbox', '')),
		("Client Inbox", m.get('client_inbox', '')),
		("Topic", m.get('topic', '')),
		("Reply Topic", m.get('reply_topic', '')),
		("Length", str(m.get('length', ''))),
		("Buffer Items", str(m.get('buffer_items', '')))
	]
	
	# Calculate the maximum width for element names
	max_name_width = max(len(name) for name, _ in elements)
	
	# Format each item with a left-aligned name and colon, followed by a line break
	for name, value in elements:
		m_str += "<b>{:<{width}}:</b> {}<br>".format(name, value, width=max_name_width)

	return m_str


# Ensure the script was called with an argument
if len(sys.argv) < 2:
	print(f"Usage: {sys.argv[0]} <path_to_log_file>")
	sys.exit(1)


# Take the log file path from the first argument
log_file_path = sys.argv[1]

methods = []
messages = []
# Open the log file and read line by line
with open(log_file_path, 'r') as file:
	for line in file:

		#print('\nLINE=%s' %(line))
		parts = line.split('[')
		header = parts[0].split()

		#buffer1_content = '[' + parts[1] if len(parts) > 1 else ''
		buffer2_content = line.split('||')[1] if '||' in line else ''

		#print("buffer2_content=%s" %(buffer2_content))

		# counter = header[0]
		# sender_inbox = header[1]
		# client_inbox = header[2]
		# topic = header[3]
		# reply_topic = header[4]
		# length = header[5]
		# buffer_items = parse_buffer(buffer2_content[1:-2])

		message = {}
		message['counter'] = header[0]
		message['sender_inbox'] = header[1]
		message['client_inbox'] = header[2]
		message['topic'] = header[3]
		message['reply_topic'] = header[4]
		message['length'] = int(header[5])
		message['buffer_items'] = parse_buffer(buffer2_content)

		message['method'] = ''
		#print(message['buffer_items'])
		for i in message['buffer_items']:
			#print("i=%s"%(i))
			if str(i).startswith('METHOD'):
				message['method'] = i[:-1]
				if message['method'] not in methods:
					methods.append(message['method'])
				break

		if message['method'] == '':
			#print("no method found")
			#print(message)
			pass

		messages.append(message)


#print(methods)

exchanges = []
nr_exchanges_found = 0

nr_getparametervalues = 0
nr_setparametervalues = 0

for message in messages:

	if message["method"] == "METHOD_GETPARAMETERVALUES":
		nr_getparametervalues+=1

	if message["method"] == "METHOD_SETPARAMETERVALUES":
		nr_setparametervalues+=1

	if message["method"] != "METHOD_RESPONSE":

		response_found = False
		for m in messages:
			if m["method"] == 'METHOD_RESPONSE' and message['sender_inbox'] == m['client_inbox'] and message['length'] > 0:
				if int(m['counter']) > int(message['counter']):
					response_found = True
					break

		nr_exchanges_found+= 1
		exchange = {}
		exchange["counter"] = nr_exchanges_found
		exchange["request"] = message

		if response_found:
			exchange["response"] = m
			#print('response found %d %d' %(int(m['counter']), int(message['counter'])))
		else:
			exchange["response"] = []
			#print('no response found %d %s' %(nr_exchanges_found, message))
			#exit()

		exchange["request_tstamp"] = 0
		exchange["response_tstamp"] = 0
		exchange["source"] = ''
		exchange["destination"] = ''
		exchange["method"] = ''
		exchange["param"] = ''
		exchange["value"] = ''
		exchange["remark"] = ''
		exchanges.append(exchange)

#print("\nfound %d messages, found %d exchanges, %d nr_getparametervalues, %d nr_setparametervalues" %(len(messages), nr_exchanges_found, nr_getparametervalues, nr_setparametervalues))

components = []

#print(len(exchanges))
for exchange in exchanges:

	request = exchange["request"]
	response = exchange["response"]

	source = request["sender_inbox"].split('.')[1] + '(' + request["sender_inbox"].split('.')[3] + ')'
	destination = request["client_inbox"].split('.')[1] + '(' + request["client_inbox"].split('.')[3]  + ')'

	exchange["source"] = source
	exchange["destination"] = destination

	request_items = request["buffer_items"]
	response_items = response["buffer_items"] if "buffer_items" in response else []

	#print()
	#print('request=%s'%request)
	#print('buffer_items=%s' %request["buffer_items"])

	if len(request["buffer_items"]) == 0:
		#exit()
		exchange["remark"] = "empty buffer"
		continue

	if len(request["method"]) == 0:
		exchange["remark"] = "empty method"
		continue

	if len(response) == 0:
		exchange["remark"] = "empty response"
		continue


	exchange["method"] = request["method"].split("METHOD_")[1]



	if source not in components:
		components.append(source)
	if destination not in components:
		components.append(destination)


	#METHOD_GETPARAMETERVALUES', 'METHOD_RESPONSE', 'METHOD_RPC', 'METHOD_GETHEALTH', 'METHOD_SUBSCRIBE', 'METHOD_GETPARAMETERNAMES', 'METHOD_SETPARAMETERATTRIBUTES', 'METHOD_SETPARAMETERVALUES']

	if request["method"] == "METHOD_GETHEALTH":
		exchange["value"] = "%s" %(response_items[0])
		exchange["remark"] = ""

	elif request["method"] == "METHOD_RPC":
		exchange["remark"] = ""
		exchange["param"] = "%s" %(request_items[1])

	elif request["method"] == "METHOD_SUBSCRIBE":
		exchange["param"] = "%s" %(request_items[0])
		exchange["remark"] = ""

	elif request["method"] == "METHOD_GETPARAMETERNAMES":
		ret = int(response_items[0])

		if ret == 102 or ret == 9005:
			exchange["param"] = "%s" %(request_items[2])
			exchange["value"] = "?"
			exchange["remark"] = "ret=%s" %ret

		else:
			#print('--------------------------------------------')
			#print()
			#print(request)
			#print()
			#print(response)
			if response_items[1] == '\x00':
				nrvalues = 0
			else:
				nrvalues = int(response_items[1])
			exchange["param"] = "%s" %(request_items[0])
			if nrvalues > 0:

				if isinstance(response_items[2], int):
					exchange["value"] = "?"
				else:
					exchange["value"] = "%s" %(response_items[2][:-1])
					if nrvalues > 1:
						exchange["value"] += " ..."
						#print(response_items)
						#print(exchange["value"])
			else:
				exchange["remark"] = "0 values returned"

	elif request["method"] == "METHOD_SETPARAMETERATTRIBUTES":
		exchange["param"] = "%s" %(request_items[2])

	elif request["method"] == "METHOD_GETPARAMETERVALUES":

		#print()
		#print()
		#print("request=%s"%request)
		#print()
		#print("response=%s"%response)

		if len(response_items) > 0:

			if isinstance(response_items[0], int):

				ret = int(response_items[0])
				if ret == 0:
					exchange["param"] = "%s" %(request_items[2])
					exchange["value"] = "%s" %(response_items[4])
					exchange["remark"] = "ret=%s" %ret

				elif ret == 3:
					exchange["remark"] = "ret=%s" %ret

				elif ret == 102:
					exchange["param"] = "%s" %(request_items[2])
					exchange["value"] = "?"
					exchange["remark"] = "ret=%s" %ret

				elif ret == 100:
					exchange["remark"] = ""
					if response_items[1] == 0:
						continue
					if response_items[1] == '\x00':
						continue

					if isinstance(response_items[1], int):

						nrvalues = int(response_items[1])
						if nrvalues > 1:

							exchange["param"] = "%s" %(request_items[2][:-1])
							if nrvalues > 1:
								exchange["param"] += " ..."

							#print(response_items[0])
							#print(response_items[4][:-1])

							if isinstance(response_items[4], int):
								exchange["value"] = "%s" %(response_items[4])
							else:
								exchange["value"] = "%s" %(response_items[4][:-1])
							if nrvalues > 1:
								exchange["value"] += " ..."

							remark = "ret=%s %s" % (ret, request_items)
						else:
							i = 0
							param = response_items[2 + i * 3][:-1]
							type = response_items[2 + i * 3 + 1]
							value = response_items[2 + i * 3 + 2]
							if type == 0: #string
								if isinstance(value, int):
									pass
								else:
									value = value[:-1]
									if value == '':
										value = "\'\'"

							elif type == 2: #?
								value = str(value)
								if value == '':
									value = "\'\'"

							elif type == 3: #bool
								if isinstance(value, int):
									pass
								else:
									value = value[:-1]
									if value == '':
										value = "\'\'"
							else:
								exchange["remark"] = "%s %s" %("?", request_items)

							exchange["param"] = param
							exchange["value"] = value


				else:
					#other error
					exchange["param"] = "%s" %(request_items[2])
					exchange["value"] = "?"
					exchange["remark"] = "ret=%s" %ret

			else:
				exchange["remark"] = "%s %s" %("?", request_items)


	elif request["method"] == "METHOD_SETPARAMETERVALUES":

		if len(request_items) > 0:

			ret = int(request_items[0])
			if ret == 0:
				#print("ret=%s" %ret)

				nrparams = int(request_items[2])

				if nrparams == 1:

					param = request_items[3][:-1]
					type = request_items[4]
					value = request_items[5]
					if value == '\x00':
						value = "\'\'"
					#param+= '[type=' + str(type) + ']'
					#param+= '[value=' + value[:-1] + ']'

					exchange["param"] = param
					exchange["value"] = value
					exchange["remark"] = ""
					#print(remark)

			else:
				print("nrparams != 1")
				print("ret=%s" %ret)
				exit()

	else:
		print('unknown method:' + request["method"])
		#exit(1)


#print(exchanges)
#print(components)

if False:
	for component in components:

		print('------------------------------------------------------------------------------')
		print(component)

		for exchange in exchanges:
			if component in exchange['source'] or component in exchange['destination']:

				print("% 20s %s %-20s : %s | %s" %(exchange["source"], "==>>    " if exchange['method'] == 'SETPARAMETERVALUES' else "    <<==", exchange["destination"], exchange["remark"], exchange["response"]["buffer_items"]))


i = 0
plain_exchanges = []
for exchange in exchanges:

	plain_exchanges.append({
		"counter": exchange["counter"],
		"source": exchange["source"],
		"destination": exchange["destination"],
		"method": exchange["method"],
		"param": exchange["param"],
		"value": exchange["value"],
		"remark": exchange["remark"],
		"request": get_message_content(exchange["request"]),
		"response": get_message_content(exchange["response"]),
	})



#print(plain_exchanges)

create_wireshark_like_html(plain_exchanges, sys.argv[1].split('.')[0] + '.html')
