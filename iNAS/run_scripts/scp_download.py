from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import time
import sys
import glob, os
import argparse
from pprint import pprint

from scp_upload import SSH, arg_parser



REMOTE_TRIAL_LOG_DIR = "trial_log/"
LOCAL_TRIAL_LOG_DIR = "../downloads/trial_logs_download/"

GPU_SERVER_SETTINGS = {   
    
    'gs154' : {
        "REMOTE_IP" : 'xxx.xxx.xxx.xxx', "REMOTE_USER" : 'username', "REMOTE_PASS" : 'password',
        "WORKING_DIR" : "/path/to/working_dir" + REMOTE_TRIAL_LOG_DIR,
        "LOCAL_DOWNLOAD_DIR" : LOCAL_TRIAL_LOG_DIR + "TEMP" + "/"
    },
}


def _download(server_name):
    print ("\n\n====================================================")
    print ("Downloading from to : ", server_name.upper())
    
    server_settings = GPU_SERVER_SETTINGS[server_name]
    ssh = SSH(server_settings['REMOTE_IP'], server_settings['REMOTE_USER'], server_settings['REMOTE_PASS'])        

    # copy folders/files            
    remote_dir = server_settings["WORKING_DIR"]
    local_dir = server_settings["LOCAL_DOWNLOAD_DIR"]
    
    print("\n---: REMOTE: ", remote_dir)
    print("\n---: LOCAL: ", local_dir)
    print ("====================================================")

    ssh.scp.get(remote_dir, local_path=local_dir, recursive=True, preserve_times=True)

    ssh.disconnect()




if __name__ == "__main__":
    
    setting_selection = arg_parser()

    server_name = setting_selection['server']

    # Parse and check the arguments    
    if server_name == 'all':    # push code to all GPU servers

        for each_server_name in GPU_SERVER_SETTINGS.keys():
            _download(each_server_name)
    else:
        _download(server_name)
        



