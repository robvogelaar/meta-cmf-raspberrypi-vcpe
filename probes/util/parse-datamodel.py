#!/usr/bin/env python3
import sys

def parse_data(data):
    lines = data.split('\n')
    parsed_data = {}
    current_component = None
    expecting_type_value = False
    param_name = None

    for line in lines:
        if line.startswith('getv from/to component'):
            current_component = line.split('(')[1].split(')')[0]
            parsed_data[current_component] = []
        elif expecting_type_value:
            parts = line.split()
            param_type = parts[1].rstrip(',')
            param_value = ' '.join(parts[3:])
            parsed_data[current_component].append({
                'name': param_name,
                'type': param_type,
                'value': param_value
            })
            expecting_type_value = False
        elif line.strip().startswith('Parameter'):
            parts = line.split()
            if len(parts) > 3:
                param_name = parts[3]
                expecting_type_value = True

    return parsed_data

def create_html(parsed_data1, filename1, parsed_data2, filename2, output_filename):
    with open(output_filename, 'w') as file:
        file.write('<html><head><style>')
        file.write('body { background-color: #e7f4ff; }')  # Very light blue background
        file.write('.collapsible { cursor: pointer; background-color: #d0e2f2; border: none; text-align: left; outline: none; font-size: 15px; display: block; margin-top: 5px; }')
        file.write('.active, .collapsible:hover { background-color: #a4c4e5; }')  # Darker shade of blue for active/hover
        file.write('.content { display: none; padding: 0 18px; margin-left: 20px; overflow: hidden; background-color: #f1f9ff; }')  # Light blue for content
        file.write('.courier { font-family: Courier, monospace; }')
        file.write('.column { float: left; width: 50%; }')
        file.write('.row:after { content: ""; display: table; clear: both; }')
        file.write('.header { font-weight: bold; margin-top: 20px; }')
        file.write('</style></head><body>')

        file.write('<div class="row">')
        file.write(f'<div class="column"><div class="header">{filename1}</div>')
        for component, parameters in parsed_data1.items():
            file.write(f'<div><button class="collapsible">{component}</button><div class="content">')
            hierarchy = build_hierarchy(parameters)
            file.write(generate_html_from_hierarchy(hierarchy))
            file.write('</div></div>')
        file.write('</div>')

        if parsed_data2:
            file.write(f'<div class="column"><div class="header">{filename2}</div>')
            for component, parameters in parsed_data2.items():
                file.write(f'<div><button class="collapsible">{component}</button><div class="content">')
                hierarchy = build_hierarchy(parameters)
                file.write(generate_html_from_hierarchy(hierarchy))
                file.write('</div></div>')
            file.write('</div>')
        
        file.write('</div>')  # Close row div

        file.write('<script>')
        file.write('var coll = document.getElementsByClassName("collapsible");')
        file.write('for (var i = 0; i < coll.length; i++) {')
        file.write('coll[i].addEventListener("click", function() {')
        file.write('this.classList.toggle("active");')
        file.write('var content = this.nextElementSibling;')
        file.write('if (content.style.display === "block") {')
        file.write('content.style.display = "none";')
        file.write('} else { content.style.display = "block"; } }); }')
        file.write('</script></body></html>')

def build_hierarchy(parameters):
    hierarchy = {}
    for param in parameters:
        parts = param['name'].replace('Device.', '').split('.')
        current_level = hierarchy
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[parts[-1]] = (param['type'], param['value'])
    return hierarchy


def generate_html_from_hierarchy(hierarchy, depth=0):
    html = ''
    for key, value in hierarchy.items():
        if isinstance(value, dict):
            html += f'<div><button class="collapsible courier">{key}</button><div class="content">'
            html += generate_html_from_hierarchy(value, depth + 1)
            html += '</div></div>'
        else:
            param_type, param_value = value
            display_value = f'{param_value} ({param_type})' if param_value else f'({param_type})'
            html += f'<div><span class="courier">{key}</span>: <span class="courier">{display_value}</span></div>'
    return html


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: script.py <filename1> [<filename2>]")
        sys.exit(1)

    filename1 = ''
    filename2 = ''

    filename1 = sys.argv[1]
    try:
        with open(filename1, 'r') as file:
            data = file.read()
            parsed_data1 = parse_data(data)
    except FileNotFoundError:
        print(f"Error: File '{filename1}' not found.")
        sys.exit(1)

    parsed_data2 = {}
    filename2 = ''
    if len(sys.argv) == 3:
        filename2 = sys.argv[2]
        try:
            with open(filename2, 'r') as file:
                data = file.read()
                parsed_data2 = parse_data(data)
        except FileNotFoundError:
            print(f"Error: File '{filename2}' not found.")
            sys.exit(1)

    output_html_filename = filename1.split('.')[0] + filename2.split('.')[0] + '.html'
    create_html(parsed_data1, filename1, parsed_data2, filename2, output_html_filename)
    print(f"{output_html_filename}")


if __name__ == "__main__":
    main()
