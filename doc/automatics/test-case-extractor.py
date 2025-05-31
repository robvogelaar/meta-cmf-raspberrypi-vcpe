#!/usr/bin/env python3
"""
Test Case Extractor and Web Generator
Extracts TC- test cases from source files and generates a sortable HTML table
"""

import os
import re
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any

class TestCaseExtractor:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.test_cases = []
        self.file_contents = {}  # Cache for file contents
        
    def extract_test_cases_with_rg(self) -> List[Dict[str, Any]]:
        """Extract test cases using ripgrep (rg) command"""
        try:
            # Use rg to find all @TestDetails patterns with testUID in Java files only
            cmd = ["rg", "-n", "--no-heading", "-A", "2", "-B", "1", "--type", "java", "@TestDetails.*testUID.*TC-"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode != 0:
                print(f"Warning: rg command failed: {result.stderr}")
                return self._extract_test_cases_fallback()
                
            return self._parse_rg_output_multiline(result.stdout)
            
        except FileNotFoundError:
            print("ripgrep (rg) not found, using fallback method")
            return self._extract_test_cases_fallback()
    
    def _parse_rg_output_multiline(self, output: str) -> List[Dict[str, Any]]:
        """Parse ripgrep output with context lines to extract test case details"""
        test_cases = []
        lines = output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line or line.startswith('--'):
                i += 1
                continue
                
            # Parse rg output format: filename:line_number:content
            parts = line.split(':', 2)
            if len(parts) < 3:
                i += 1
                continue
                
            filename = parts[0]
            line_number = parts[1]
            content = parts[2]
            
            # Check if this line contains @TestDetails
            if '@TestDetails' in content:
                # Combine current line with next few lines to get complete annotation
                full_annotation = content
                j = i + 1
                while j < len(lines) and j < i + 5:  # Look ahead up to 5 lines
                    next_line = lines[j]
                    if ':' in next_line and (next_line.split(':', 1)[0] == filename):
                        # Same file, add content
                        next_content = next_line.split(':', 2)[-1]
                        full_annotation += " " + next_content.strip()
                        if ')' in next_content:  # End of annotation
                            break
                    j += 1
                
                # Extract testUID and description from full annotation
                uid_match = re.search(r'testUID\s*=\s*["\']([^"\']+)["\']', full_annotation)
                if uid_match:
                    test_uid = uid_match.group(1)
                    if test_uid.startswith('TC-'):
                        # Handle escaped quotes in description
                        desc_match = re.search(r'testDecription\s*=\s*"((?:[^"\\\\]|\\\\.)*)"', full_annotation)
                        if not desc_match:
                            desc_match = re.search(r"testDecription\s*=\s*'((?:[^'\\\\]|\\\\.)*)'", full_annotation)
                        description = desc_match.group(1) if desc_match else ""
                        
                        test_cases.append({
                            'test_uid': test_uid,
                            'filename': filename,
                            'line_number': int(line_number),
                            'description': description,
                            'content_snippet': full_annotation.strip()
                        })
                        
                        # Cache the file content if not already cached
                        if filename not in self.file_contents:
                            try:
                                file_path = self.base_dir / filename
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    self.file_contents[filename] = f.read()
                            except Exception as e:
                                print(f"Warning: Could not read file {filename}: {e}")
                                self.file_contents[filename] = f"// Error reading file: {e}"
            
            i += 1
            
        return test_cases
    
    def _cache_all_test_files(self):
        """Cache content for all files that have test cases"""
        print("Caching file contents...")
        unique_files = set(tc['filename'] for tc in self.test_cases)
        
        for filename in unique_files:
            if filename not in self.file_contents:
                try:
                    file_path = self.base_dir / filename
                    print(f"Reading file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self.file_contents[filename] = content
                        print(f"Cached {len(content)} characters for {filename}")
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
                    self.file_contents[filename] = f"// Error reading file: {e}"
        
        print(f"Total files cached: {len(self.file_contents)}")
        for filename in self.file_contents.keys():
            print(f"  - {filename}")
    
    def _extract_description(self, filename: str, line_number: int, content: str) -> str:
        """Extract test description from annotation or nearby lines"""
        # Try to extract from current line first - handle escaped quotes
        desc_match = re.search(r'testDecription\s*=\s*"((?:[^"\\\\]|\\\\.)*)"', content)
        if not desc_match:
            desc_match = re.search(r"testDecription\s*=\s*'((?:[^'\\\\]|\\\\.)*)'", content)
        if desc_match:
            return desc_match.group(1)
        
        # Try to read the file and look for description in nearby lines
        try:
            file_path = self.base_dir / filename
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Look in a window around the current line
            start_line = max(0, line_number - 5)
            end_line = min(len(lines), line_number + 3)
            
            for i in range(start_line, end_line):
                line = lines[i]
                desc_match = re.search(r'testDecription\s*=\s*"((?:[^"\\\\]|\\\\.)*)"', line)
                if not desc_match:
                    desc_match = re.search(r"testDecription\s*=\s*'((?:[^'\\\\]|\\\\.)*)'", line)
                if desc_match:
                    return desc_match.group(1)
                    
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            
        return ""
    
    def _extract_test_cases_fallback(self) -> List[Dict[str, Any]]:
        """Fallback method using Python file traversal"""
        test_cases = []
        
        # Search for Java files
        for java_file in self.base_dir.rglob("*.java"):
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Find all @TestDetails annotations with testUID
                testdetails_pattern = r'@TestDetails\([^)]*testUID\s*=\s*["\']([^"\']+)["\'][^)]*\)'
                matches = re.finditer(testdetails_pattern, content, re.DOTALL)
                
                for match in matches:
                    test_uid = match.group(1)
                    if not test_uid.startswith('TC-'):
                        continue
                        
                    # Find line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Extract description from the same annotation - handle escaped quotes
                    annotation_text = match.group(0)
                    desc_match = re.search(r'testDecription\s*=\s*"((?:[^"\\\\]|\\\\.)*)"', annotation_text)
                    if not desc_match:
                        desc_match = re.search(r"testDecription\s*=\s*'((?:[^'\\\\]|\\\\.)*)'", annotation_text)
                    description = desc_match.group(1) if desc_match else ""
                    
                    test_cases.append({
                        'test_uid': test_uid,
                        'filename': str(java_file.relative_to(self.base_dir)),
                        'line_number': line_number,
                        'description': description,
                        'content_snippet': content[max(0, match.start()-50):match.end()+50].replace('\n', ' ')
                    })
                    
                    # Cache the file content if not already cached
                    filename_key = str(java_file.relative_to(self.base_dir))
                    if filename_key not in self.file_contents:
                        self.file_contents[filename_key] = content
                    
            except Exception as e:
                print(f"Error processing {java_file}: {e}")
                
        return test_cases
    
    def generate_html_report(self, output_file: str = "test_cases_report.html"):
        """Generate an HTML report with sortable table"""
        
        # Extract test cases
        self.test_cases = self.extract_test_cases_with_rg()
        
        # Read all file contents for any files we haven't cached yet
        self._cache_all_test_files()
        
        # Store the search path for JavaScript
        search_path_js = str(self.base_dir.absolute()).replace('\\', '/')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Cases Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 150px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .search-container {{
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .search-input {{
            padding: 10px;
            width: 300px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
        
        .table-container {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        
        th:hover {{
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }}
        
        th.sortable::after {{
            content: ' ↕';
            opacity: 0.5;
        }}
        
        th.sort-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        
        th.sort-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }}
        
        tr:hover {{
            background-color: #f8f9ff;
        }}
        
        .test-uid {{
            font-weight: bold;
            color: #667eea;
        }}
        
        .filename {{
            font-family: monospace;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            word-break: break-all;
            cursor: pointer;
            color: #0066cc;
            text-decoration: underline;
        }}
        
        .filename:hover {{
            background: #e9ecef;
            color: #0052a3;
        }}
        
        .line-number {{
            text-align: center;
            font-family: monospace;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        
        .description {{
            max-width: 400px;
            word-wrap: break-word;
        }}
        
        .snippet {{
            font-family: monospace;
            font-size: 0.85em;
            color: #666;
            max-width: 300px;
            word-wrap: break-word;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}
        
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        
        .modal-content {{
            background-color: #fefefe;
            margin: 2% auto;
            padding: 0;
            border-radius: 10px;
            width: 90%;
            height: 90%;
            max-width: 1200px;
            display: flex;
            flex-direction: column;
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .modal-title {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .close {{
            background: none;
            border: none;
            color: white;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .close:hover {{
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
        }}
        
        .modal-body {{
            flex: 1;
            padding: 20px;
            overflow: auto;
        }}
        
        .file-content {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 100%;
            overflow: auto;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .highlighted-line {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding-left: 10px;
            margin-left: -10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Cases Report</h1>
        <p>Extracted from RDKB Test Suite</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(self.test_cases)}</div>
            <div>Total Test Cases</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(tc['filename'] for tc in self.test_cases))}</div>
            <div>Files</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len([tc for tc in self.test_cases if tc['description'] != ""])}</div>
            <div>With Descriptions</div>
        </div>
    </div>
    
    <div class="search-container">
        <input type="text" id="searchInput" class="search-input" placeholder="🔍 Search test cases...">
    </div>
    
    <div class="table-container">
        <table id="testCasesTable">
            <thead>
                <tr>
                    <th class="sortable" data-column="test_uid">Test UID</th>
                    <th class="sortable" data-column="filename">Filename</th>
                    <th class="sortable" data-column="description">Description</th>
                    <th class="sortable" data-column="content_snippet">Code Snippet</th>
                </tr>
            </thead>
            <tbody id="tableBody">
                <!-- Table content will be generated by JavaScript -->
            </tbody>
        </table>
        <div id="noResults" class="no-results" style="display: none;">
            No test cases found matching your search.
        </div>
    </div>

    <!-- Modal for file viewer -->
    <div id="fileModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">File Viewer</div>
                <button class="close" id="closeModal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="file-content" id="fileContent">
                    <div class="loading">Loading file...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const testCases = {json.dumps(self.test_cases)};
        const searchPath = "{search_path_js}";
        const fileContents = {json.dumps(self.file_contents)};
        let currentSort = {{ column: null, direction: 'asc' }};
        let filteredCases = [...testCases];

        // Modal functionality
        const modal = document.getElementById('fileModal');
        const closeModal = document.getElementById('closeModal');
        
        function openFile(filename, lineNumber = null) {{
            const modalTitle = document.getElementById('modalTitle');
            const fileContent = document.getElementById('fileContent');
            
            modalTitle.textContent = filename + (lineNumber ? ` (Line ${{lineNumber}})` : '');
            
            if (fileContents[filename]) {{
                const content = fileContents[filename];
                const lines = content.split('\\n');
                
                let formattedContent = '';
                lines.forEach((line, index) => {{
                    const lineNum = index + 1;
                    const isHighlighted = lineNumber && Math.abs(lineNum - lineNumber) <= 2;
                    const className = (lineNumber && lineNum === lineNumber) ? 'highlighted-line' : '';
                    
                    formattedContent += `<div class="${{className}}">${{String(lineNum).padStart(4, ' ')}}: ${{line.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>`;
                }});
                
                fileContent.innerHTML = formattedContent;
                
                // Scroll to the highlighted line
                if (lineNumber) {{
                    setTimeout(() => {{
                        const highlightedElement = fileContent.querySelector('.highlighted-line');
                        if (highlightedElement) {{
                            highlightedElement.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        }}
                    }}, 100);
                }}
            }} else {{
                fileContent.innerHTML = '<div class="loading">File content not available</div>';
            }}
            
            modal.style.display = 'block';
        }}
        
        closeModal.addEventListener('click', function() {{
            modal.style.display = 'none';
        }});
        
        window.addEventListener('click', function(event) {{
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }});

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            filteredCases = testCases.filter(tc => 
                tc.test_uid.toLowerCase().includes(searchTerm) ||
                tc.filename.toLowerCase().includes(searchTerm) ||
                tc.description.toLowerCase().includes(searchTerm) ||
                tc.content_snippet.toLowerCase().includes(searchTerm)
            );
            renderTable();
        }});

        // Sorting functionality
        document.querySelectorAll('th.sortable').forEach(th => {{
            th.addEventListener('click', function() {{
                const column = this.dataset.column;
                
                if (currentSort.column === column) {{
                    currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                }} else {{
                    currentSort.column = column;
                    currentSort.direction = 'asc';
                }}
                
                // Update header styles
                document.querySelectorAll('th').forEach(header => {{
                    header.classList.remove('sort-asc', 'sort-desc');
                }});
                this.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
                
                // Sort data
                filteredCases.sort((a, b) => {{
                    let aVal = a[column];
                    let bVal = b[column];
                    
                    // Handle numeric columns
                    if (column === 'line_number') {{
                        aVal = parseInt(aVal);
                        bVal = parseInt(bVal);
                    }}
                    
                    if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
                    if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
                    return 0;
                }});
                
                renderTable();
            }});
        }});

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            const noResults = document.getElementById('noResults');
            
            if (filteredCases.length === 0) {{
                tbody.innerHTML = '';
                noResults.style.display = 'block';
                return;
            }}
            
            noResults.style.display = 'none';
            tbody.innerHTML = filteredCases.map(tc => `
                <tr>
                    <td class="test-uid">${{tc.test_uid}}</td>
                    <td class="filename" onclick="openFile('${{tc.filename}}', ${{tc.line_number}})">${{tc.filename}}</td>
                    <td class="description">${{tc.description}}</td>
                    <td class="snippet">${{tc.content_snippet}}</td>
                </tr>
            `).join('');
        }}

        // Initial render
        renderTable();
    </script>
</body>
</html>
        """
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"HTML report generated: {output_file}")
        print(f"Found {len(self.test_cases)} test cases")
        
        return output_file

def main():
    """Main function to run the extractor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract test cases and generate HTML report')
    parser.add_argument('--dir', '-d', default='.', help='Base directory to search (default: current directory)')
    parser.add_argument('--output', '-o', default='test_cases_report.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    extractor = TestCaseExtractor(args.dir)
    output_file = extractor.generate_html_report(args.output)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📁 Output file: {output_file}")
    print(f"🌐 Open in browser: file://{os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()