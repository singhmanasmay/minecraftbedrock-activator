"""
Minecraft Bedrock Edition Activator
This script helps activate Minecraft Bedrock Edition by replacing the Windows.ApplicationModel.Store.dll
with a modified version. Requires administrator privileges to run.
"""

import os  # For file and path operations
import shutil  # For file copying
import time  # For adding delays
import subprocess  # For running system commands
import msvcrt  # For handling keyboard input (Windows-specific)
import pyuac  # For handling administrator privileges
import handlecatcher  # Custom module to handle file processes
#pywin32

# Global flag to track first-time initialization
init = True

def activate():
    """Main function that handles the Minecraft Bedrock activation process.
    This function performs the following steps:
    1. Checks for administrator privileges
    2. Verifies system directories existence
    3. Takes ownership of DLL files
    4. Modifies file permissions
    5. Terminates processes using the DLL
    6. Replaces DLL files with modified versions
    """
    global init

    # Check for administrator privileges
    if pyuac.isUserAdmin():
        admin = True
    else: admin = False

    # Verify existence of system directories
    if os.path.exists(os.path.join(os.environ['WINDIR'],'SYSTEM32')):
        system32exists = True
    else: system32exists = False
    if os.path.exists(os.path.join(os.environ['WINDIR'],'SYSWOW64')):
        syswow64exists = True
    else: syswow64exists = False

    # Display banner and system information on first run
    if init:
        init = False
        print('\n'.join(['██████╗░░█████╗░██╗░░░░░███████╗██████╗░░░███╗░░░█████╗░███╗░░██╗',
                         '██╔══██╗██╔══██╗██║░░░░░██╔════╝██╔══██╗░████║░░██╔══██╗████╗░██║',
                         '██████╦╝███████║██║░░░░░█████╗░░██████╔╝██╔██║░░██║░░██║██╔██╗██║',
                         '██╔══██╗██╔══██║██║░░░░░██╔══╝░░██╔══██╗╚═╝██║░░██║░░██║██║╚████║',
                         '██████╦╝██║░░██║███████╗███████╗██║░░██║███████╗╚█████╔╝██║░╚███║',
                         '╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░╚═╝╚══════╝░╚════╝░╚═╝░░╚══╝','https://github.com/singhmanasmay','\n']))
        print(f'administrator granted= {admin}')
        print(f'system32 exists= {system32exists}')
        print(f'syswow64 exists= {syswow64exists}')

    # Main activation logic
    if admin:
        if system32exists:
            try:
                # Take ownership of System32 DLL
                print(str(subprocess.check_output(r'takeown /f "C:\Windows\System32\Windows.ApplicationModel.Store.dll" /a'),'utf-8'))
                if syswow64exists:
                    # Take ownership of SysWOW64 DLL if it exists
                    print(str(subprocess.check_output(r'takeown /f "C:\Windows\SysWOW64\Windows.ApplicationModel.Store.dll" /a'),'utf-8'))
                time.sleep(2)  # Wait for ownership changes to take effect

                # Grant modify permissions to administrators
                print(str(subprocess.check_output(r'icacls "C:\Windows\System32\Windows.ApplicationModel.Store.dll" /grant Administrators:(M)'),'utf-8'))
                if syswow64exists:
                    print(str(subprocess.check_output(r'icacls "C:\Windows\SysWOW64\Windows.ApplicationModel.Store.dll" /grant Administrators:(M)'),'utf-8'))

                # Kill processes that are using the DLL files
                for pid in handlecatcher.handlecatcher(r"C:\Windows\System32\Windows.ApplicationModel.Store.dll"):
                    print(str(subprocess.check_output(f'taskkill /f /pid {pid}'),'utf-8'))
                if syswow64exists:
                    for pid in handlecatcher.handlecatcher(r"C:\Windows\SysWOW64\Windows.ApplicationModel.Store.dll"):
                        print(str(subprocess.check_output(f'taskkill /f /pid {pid}'),'utf-8'))
                time.sleep(3)  # Wait for processes to terminate

                # Replace original DLL with modified version
                shutil.copy2(os.path.join(os.path.dirname(__file__),r'payload\System32\Windows.ApplicationModel.Store.dll'),os.path.join(os.environ['WINDIR'],'SYSTEM32'))
                print('system32 patched')
                if syswow64exists:
                    shutil.copy2(os.path.join(os.path.dirname(__file__),r'payload\SysWOW64\Windows.ApplicationModel.Store.dll'),os.path.join(os.environ['WINDIR'],'SYSWOW64'))
                    print('syswow64 patched\n')
                print('Minecraft Bedrock Activated.\nPlease restart Minecraft Bedrock.')
            except Exception as e:
                # Handle any errors during the activation process
                print(e)
                print('An unexpected error occurred.\nPlease report at:\nhttps://github.com/singhmanasmay/minecraftbedrock-activator/issues')
        else:
            # System32 directory not found - likely not Windows
            print('Unsupported OS\nPlease ensure you are running this script on a Windows system.')
    else:
        # Not running with admin privileges
        print('Administrator privileges not granted.\nPlease run this script as an administrator.')
    
    # Wait for user input before closing
    print('Press any key to exit...')
    msvcrt.getch()

# Script entry point
if not pyuac.isUserAdmin():
    try:
        pyuac.runAsAdmin()  # Try to restart with admin privileges
    except:
        activate()  # If elevation fails, run anyway
else:
    activate()  # Already running as admin
