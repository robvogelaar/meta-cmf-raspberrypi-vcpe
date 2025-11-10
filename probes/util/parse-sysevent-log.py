#!/usr/bin/env python3

import sys, os, json, datetime, glob, re


def create_wireshark_like_html(exchanges, handles, htmlfilename):
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
            overflow: auto;
            flex-grow: 1;
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
        .id {
            margin: 0 5px;
            min-width: 20px; /* Adjust width as needed */
        }
        .handle {
            margin: 0 5px;
            min-width: 200px; /* Adjust width as needed */
        }
        .cmd {
            margin: 0 5px;
            min-width: 250px; /* Adjust width as needed */
        }
        .params {
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
                <span class="id" data-sort="id">id</span>
                <span class="handle" data-sort="handle">handle</span>
                <span class="cmd" data-sort="cmd">cmd</span>
                <span class="params" data-sort="params">params</span>
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


    function getIdHandleCmdColor(id, handle, cmd) {
        var key = id + '-' + handle + '-' + cmd;
        if (!colorMap[key]) {
            // Generate a random color
            colorMap[key] = 'hsl(' + Math.random() * 360 + ', 70%, 80%)';
        }
        return colorMap[key];
    }


    function showDetails(exchange, element) {
        var requestDiv = document.getElementById("requestDiv");
        var responseDiv = document.getElementById("responseDiv");

        requestDiv.innerHTML = "<b>id:</b> " + exchange.id;
        requestDiv.innerHTML += "<br><b>handle:</b> " + exchange.handle;
        requestDiv.innerHTML += "<br><b>process:</b> " + exchange.process;
        requestDiv.innerHTML += "<br><b>parent:</b> " + exchange.parent;

        requestDiv.innerHTML += "<br><b>async actions:</b>";
        handles[exchange.id].async_action_registrations.forEach(item => {
            requestDiv.innerHTML += '<br>' + item;
        });

        requestDiv.innerHTML += "<br><b>async messages:</b>";
        handles[exchange.id].async_message_registrations.forEach(item => {
            requestDiv.innerHTML += '<br>' + item;
        });


        //responseDiv.innerHTML = handles[exchange.id].handle;
        //responseDiv.innerHTML = handles[exchange.id].async_action_registrations;


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
        div.style.backgroundColor = getIdHandleCmdColor(exchange.id, exchange.handle, exchange.cmd);

        div.appendChild(createSpan("stamp", exchange.stamp || ""));
        div.appendChild(createSpan("id", exchange.id || ""));
        div.appendChild(createSpan("handle", exchange.handle || ""));
        div.appendChild(createSpan("cmd", exchange.cmd || ""));
        div.appendChild(createSpan("params", exchange.params || ""));

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

    var handles = """ + str(handles) + """;

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


def find_next_line(lines, l, match, match_index, extra, extra_index):

    found = False
    for m in range(l + 1, l + 150):
        if m == len(lines):
            break

        if re.match(match, lines[m][match_index]):
            if extra == '' or re.match(extra, lines[m][extra_index]):
                found = True
                break
    if found:
        pass
    else:
        print('next line not found: %s, %d, %s, %d' %(match, match_index, extra, extra_index))
        print(lines[l])
        exit()

    return found, m


def find_prev_line(lines, l, match, match_index, extra, extra_index):

    found = False
    for m in range(l - 1, l - 150, -1):
        if m == 0:
            break

        if re.match(match, lines[m][match_index]):
            if extra == '' or re.match(extra, lines[m][extra_index]):
                found = True
                break
    if found:
        pass
    else:
        print('prev line not found: %s, %d, %s, %d' %(match, match_index, extra, extra_index))
        print(lines[l])
        exit()

    return found, m


def main():

    # Ensure the script was called with an argument
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_log_file>")
        sys.exit(1)

    # Take the log file path from the first argument
    log_file_path = sys.argv[1]


    lines = {}
    i = 0
    with open(log_file_path, 'r') as file:
        for line in file:
            if 'sysevent' in line or 'SE_MSG' in line:
                pass
            else:
                print('unparsed line, linenr: %d %s' %(i+1, line))
                print('exiting prematurely') 
                exit()

            lines[i] = [line[:-1].split(" ", 1)[0]] + line[:-1].split(" ", 1)[1].split('|')[1:]

            i+= 1
            #if i == 1000:
            #   break

    first_stamp = None

    handles = {}
    async_action_registrations = {}
    async_message_registrations = {}

    async_action_invocations = {}
    async_message_invocations = {}

    sysevents = []
    for l in lines:

        #print(l, lines[l])

        stamp = float(lines[l][0])

        if not first_stamp:
            first_stamp = stamp

        stamp = round(stamp - first_stamp, 9)

        #if stamp > 120:
        #   print('stopped log collection at tstamp 120')
        #   break

        cmd = lines[l][1]

        #print(cmd)

        ##
        if cmd == 'SE_MSG_OPEN_CONNECTION':
            found, n = find_next_line(lines, l, r'SE_MSG_OPEN_CONNECTION_REPLY', 1, '', 0)
            id = int(lines[n][2], 16)
            found, n = find_next_line(lines, l, r'sysevent_open|sysevent_local_open', 1, str(id), 2)

            #print('lines[m]=%s' %(lines[n]))
            handles[id] = {}
            handles[id]["handle"] = lines[l][2]
            handles[id]["process"] = lines[n][3]
            handles[id]["parent"] = lines[n][4]
            handles[id]["async_action_registrations"] = []
            handles[id]["async_message_registrations"] = []

            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = ""
            sysevents.append(sysevent)

        elif cmd == 'SE_MSG_OPEN_CONNECTION_REPLY':
            pass
        elif cmd == 'SE_MSG_CLOSE_CONNECTION':
            pass
        elif cmd == 'SE_MSG_NEW_CLIENT':
            pass

        ##
        elif cmd == 'SE_MSG_GET':
            found, n = find_next_line(lines, l, r'SE_MSG_GET_REPLY', 1, lines[l][2], 2)
            found, p = find_prev_line(lines, l, r'sysevent_get', 1, '', 0)
            id = int(lines[p][2])
            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = lines[l][2] + '=\"' + lines[n][3] + '\"'
            sysevents.append(sysevent)
        elif cmd == 'SE_MSG_GET_REPLY':
            pass

        ##
        elif cmd == 'SE_MSG_SET':
            found, n = find_next_line(lines, l, r'SE_MSG_SET_REPLY', 1, '', 0)
            found, p = find_prev_line(lines, l, r'sysevent_set', 1, '', 0)
            id = int(lines[p][2])
            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = lines[l][2] + '=\"' + lines[l][3] + '\"'
            sysevents.append(sysevent)
        elif cmd == 'SE_MSG_SET_REPLY':
            pass

        ##
        elif cmd == 'SE_MSG_ITERATE_GET':
            found, n = find_next_line(lines, l, 'SE_MSG_ITERATE_GET_REPLY', 1, '', 0)
            found, p = find_prev_line(lines, l, r'sysevent_get_unique', 1, '', 0)
            id = int(lines[p][2])
            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = lines[l][2] + ' = \"' + lines[l][3] + '\"'
            sysevents.append(sysevent)
        elif cmd == 'SE_MSG_ITERATE_GET_REPLY':
            pass

        ##
        elif cmd == 'SE_MSG_NOTIFICATION':
            pass

        elif cmd == 'SE_MSG_REMOVE_ASYNC':
            #1998231.992293483 |sysevent_rmcallback|14
            #1998231.992351799 |SE_MSG_REMOVE_ASYNC|0x25000000 0x1000000|

            found, p = find_prev_line(lines, l, r'sysevent_rmcallback', 1, '', 0)
            id = int(lines[p][2])
            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = ""
            sysevents.append(sysevent)

            #print(lines[l])
            if lines[l][2] != '0x0 0x0':
                del async_action_registrations[lines[l][2]]


        elif cmd == 'SE_MSG_RUN_EXTERNAL_EXECUTABLE':
            #2167182.036721772 |sysevent_set|212
            #2167182.036797213 |SE_MSG_SET|ipv6_nameserver|2001:dbe:0:1::129 |
            #2167182.036853756 |SE_MSG_RUN_EXTERNAL_EXECUTABLE|0x6f000000 0x1000000|0x0|ipv6_nameserver|2001:dbe:0:1::129|

            found, p = find_prev_line(lines, l, r'SE_MSG_SET', 1, lines[l][4], 2)
            scmd = lines[p][2] + '=' + lines[p][3]
            found, p = find_prev_line(lines, p, r'sysevent_set', 1, '', 0)
            sid = int(lines[p][2])

            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = ""
            sysevent["handle"] = ""
            sysevent["cmd"] = cmd
            sysevent["process"] = ""
            sysevent["parent"] = ""
            sysevent["params"] = ','.join(lines[l][2:6]) + '=>' + ','.join(async_action_registrations[lines[l][2]]["params"]) + '<=' + str(id)
            sysevents.append(sysevent)

            if not lines[l][2] in async_action_invocations:
                async_action_invocations[lines[l][2]] = {}

            if not "entries" in async_action_invocations[lines[l][2]]:
                async_action_invocations[lines[l][2]]["entries"] = []
            async_action_invocations[lines[l][2]]["entries"].append(id)

            for id in handles:
                for r in handles[id]["async_action_registrations"]:

                    #print('r=%s'%r)
                    #print(lines[l][2])
                    #print(lines[l])
                    #exit()

                    if r[4] == lines[l][2]:
                        handles[id]["async_action_registrations"][handles[id]["async_action_registrations"].index(r)].append('<br>&nbsp;&nbsp;&nbsp;&nbsp;<<==' + handles[sid]["handle"] + ',' + scmd + '|' + handles[sid]["process"] )


        elif cmd == 'SE_MSG_SEND_NOTIFICATION':
            #2167183.341555254 |sysevent_set|245
            #2167183.341684038 |SE_MSG_SET|lease_resync|(null)|
            #2167183.341752854 |SE_MSG_SEND_NOTIFICATION|0xa5000000 0x1000000|0x0|lease_resync|(null)|

            found, p = find_prev_line(lines, l, r'SE_MSG_SET', 1, lines[l][4], 2)
            scmd = lines[p][2] + '=' + lines[p][3]
            found, p = find_prev_line(lines, p, r'sysevent_set', 1, '', 0)
            sid = int(lines[p][2])

            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = ""
            sysevent["handle"] = ""
            sysevent["cmd"] = cmd
            sysevent["process"] = ""
            sysevent["parent"] = ""
            sysevent["params"] = ','.join(lines[l][2:6]) + '=>' + ','.join(async_message_registrations[lines[l][2]]["params"])
            sysevents.append(sysevent)

            if not lines[l][2] in async_message_invocations:
                async_message_invocations[lines[l][2]] = {}

            if not "entries" in async_message_invocations[lines[l][2]]:
                async_message_invocations[lines[l][2]]["entries"] = []
            async_message_invocations[lines[l][2]]["entries"].append(id)

            for id in handles:
                for r in handles[id]["async_message_registrations"]:
                    #print('r=%s'%r)
                    if r[2] == lines[l][2]:
                        handles[id]["async_message_registrations"][handles[id]["async_message_registrations"].index(r)].append('<br>&nbsp;&nbsp;&nbsp;&nbsp;<<==' + handles[sid]["handle"] + ',' + scmd + '|' + handles[sid]["process"] )


        ##
        elif cmd == 'SE_MSG_SET_ASYNC_ACTION':
            #1998231.907459724 |sysevent_setcallback|2
            #1998231.907513478 |SE_MSG_SET_ASYNC_ACTION|0x0|1|bridge-start|/etc/utopia/service.d/service_bridge.sh|
            #1998231.907558513 |SE_MSG_SET_ASYNC_REPLY|0x3000000 0x1000000|

            found, n = find_next_line(lines, l, r'SE_MSG_SET_ASYNC_REPLY', 1, '', 0)
            found, p = find_prev_line(lines, l, r'sysevent_setcallback', 1, '', 0)
            id = int(lines[p][2])

            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = ','.join(lines[l][2:6]) + ' = ' + lines[n][2]
            sysevents.append(sysevent)

            async_action_registrations[lines[n][2]] = {}
            async_action_registrations[lines[n][2]]["params"] = lines[l][2:6]

            handles[id]["async_action_registrations"].append(lines[l][2:6] + [lines[n][2]])



        elif cmd == 'SE_MSG_SET_ASYNC_MESSAGE':
            #1998234.386701746 |sysevent_setnotification|74
            #1998234.386868520 |SE_MSG_SET_ASYNC_MESSAGE|0x0|lan-status|
            #1998234.386920735 |SE_MSG_SET_ASYNC_REPLY|0x4e000000 0x4000000|

            found, n = find_next_line(lines, l, 'SE_MSG_SET_ASYNC_REPLY', 1, '', 0)
            found, p = find_prev_line(lines, l, r'sysevent_setnotification', 1, '', 0)
            id = int(lines[p][2])

            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = ','.join(lines[l][2:4]) + ' = ' + lines[n][2]
            sysevents.append(sysevent)

            async_message_registrations[lines[n][2]] = {}
            async_message_registrations[lines[n][2]]["params"] = lines[l][2:4] +  ['(' + handles[id]["handle"] + ')']

            handles[id]["async_message_registrations"].append(lines[l][2:4] + [lines[n][2]])


        elif cmd == 'SE_MSG_SET_ASYNC_REPLY':
            pass

        ##
        elif cmd == 'SE_MSG_SET_OPTIONS':

            #1998231.907794825 |sysevent_set_options|2
            #1998231.907848015 |SE_MSG_SET_OPTIONS|bridge-start|0x2|
            #1998231.907886305 |SE_MSG_SET_OPTIONS_REPLY|

            found, n = find_next_line(lines, l, 'SE_MSG_SET_OPTIONS_REPLY', 1, '', 0)
            found, p = find_prev_line(lines, l, r'sysevent_set_options', 1, '', 0)
            id = int(lines[p][2])
            sysevent = {}
            sysevent["stamp"] = stamp
            sysevent["id"] = id
            sysevent["handle"] = handles[id]["handle"]
            sysevent["cmd"] = cmd
            sysevent["process"] = handles[id]["process"]
            sysevent["parent"] = handles[id]["parent"]
            sysevent["params"] = lines[l][2] + '=\"' + lines[l][3] + '\"'
            sysevents.append(sysevent)

        elif cmd == 'SE_MSG_SET_OPTIONS_REPLY':
            pass

        elif cmd.startswith('sysevent_'):
            pass

        else:
            print('UNKNOWN COMMAND')
            print(lines[l])
            exit()


    #for handle in handles:
    #   print(handle, handles[handle])

    ##data = {}
    ##with open(log_file_path, 'r') as file:
    ##  lines = file.readlines()
    ##
    ##  for l in range(len(lines)):
    ##      #print(lines[l][:-1])
    ##
    ##      parts = lines[l][:-1].split(" ", 1)
    ##      cmd = parts[0]
    ##      params = parts[1]
    ##      if CMD == 'SE_MSG_GET':
    ##          name = params.split('|')[0]
    ##          if l + 1 <= len(lines):
    ##              if lines[l + 1]


    #for sysevent in sysevents:
    #   print(sysevent)

    #print(handles[1])

    #print('---')

    #for async_action_registration in async_action_registrations:
    #   print(async_action_registrations[async_action_registration])

    #print(async_action_registrations)

    #print('---')

    #for async_action_invocation in async_action_invocations:
    #   print(async_action_invocation, async_action_invocations[async_action_invocation])

    #print('---')

    #for async_message_invocation in async_message_invocations:
    #   print(async_message_invocation, async_message_invocations[async_message_invocation])

    create_wireshark_like_html(sysevents, handles, sys.argv[1].split('.')[0] + '.html')


if __name__ == '__main__':
    main()
