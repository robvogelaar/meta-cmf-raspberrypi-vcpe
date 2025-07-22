#!/usr/bin/env python3
"""
##########################################################################
# If not stated otherwise in this file or this component's Licenses.txt
# file the following copyright and licenses apply:
#
# Copyright 2021 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################

Script to create rdk-test-tool.war from TDK repositories
"""

import os
import sys
import subprocess
import shutil
import time

def execute_command(command):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing command: {command}")
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout
    except Exception as e:
        print(f"Exception executing command: {command}")
        print(f"Exception: {str(e)}")
        sys.exit(1)

def main():
    """Main function to create TDK war file"""
    
    # Get tag name from command line argument
    if len(sys.argv) > 1:
        tag_name = sys.argv[1]
    else:
        tag_name = "rdk-next"
    
    print(f"Creating TDK war file for tag: {tag_name}")
    
    # Change to /mnt directory
    os.chdir("/mnt")
    
    # Clone TDK repositories
    print("Cloning TDK-UI repository...")
    execute_command(f"git clone https://code.rdkcentral.com/r/rdk/tools/tdk/TDK-UI -b {tag_name}")
    
    print("Cloning TDK repository...")
    execute_command(f"git clone https://code.rdkcentral.com/r/rdk/tools/tdk -b {tag_name}")
    
    # Change to TDK-UI directory
    os.chdir("/mnt/TDK-UI")
    
    # Copy required files
    print("Copying TDK framework files...")
    shutil.copytree("/mnt/tdk/framework", "framework")
    
    # Build configuration
    print("Building TDK Test Manager...")
    
    # Set environment variables
    os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
    os.environ['GRAILS_HOME'] = '/usr/lib/jvm/grails-2.4.0'
    os.environ['PATH'] = f"{os.environ['GRAILS_HOME']}/bin:{os.environ['JAVA_HOME']}/bin:{os.environ['PATH']}"
    
    # Clean and compile
    print("Running grails clean...")
    execute_command("grails clean")
    
    print("Running grails compile...")
    execute_command("grails compile")
    
    print("Running grails war...")
    execute_command("grails war rdk-test-tool.war")
    
    # Copy war file to /mnt
    print("Copying war file...")
    shutil.copy("rdk-test-tool.war", "/mnt/rdk-test-tool.war")
    
    # Copy SQL dump if exists
    sql_dump = "framework/grails-app/utils/rdktestproddbdump.sql"
    if os.path.exists(sql_dump):
        print("Copying SQL dump...")
        shutil.copy(sql_dump, "/mnt/rdktestproddbdump.sql")
    
    print("TDK war creation completed successfully!")
    
    # Clean up
    os.chdir("/mnt")
    shutil.rmtree("/mnt/TDK-UI", ignore_errors=True)
    shutil.rmtree("/mnt/tdk", ignore_errors=True)

if __name__ == "__main__":
    main()