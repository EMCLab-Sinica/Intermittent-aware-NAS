from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import time
import sys
import glob, os
import argparse
from pprint import pprint

def get_dir_files(d, ftype):
    fl = []
    for f in os.listdir(d):        
        if f.endswith(ftype):
            fl.append(os.path.join(d, f))
        
    return fl


GPU_SERVER_SETTINGS = {   
    
    'gs154' : {
        "REMOTE_IP" : 'xxx.xxx.xxx.xxx', "REMOTE_USER" : 'username', "REMOTE_PASS" : 'password',
        "WORKING_DIR" : "/path/to/working_dir/",
    },    
}

def get_copy_list(working_dir):
    # <folder/file, dest_base_dir, recursive>
    copy_list = [    
        ("CostModel", working_dir, True),    
        ("IEExplorer", working_dir, True),
        #("NASBase", working_dir, True),        
        ("settings_files", working_dir, True),
        ("run_scripts", working_dir, True),
        ("misc_scripts", working_dir, True),

        # top level files
        ("main.py", working_dir, False),
        ("settings.py", working_dir, False),        
        ("clean_all.sh", working_dir, False),        
        ("clean_temp.sh", working_dir, False),        
        ]

    copy_list.extend([(f, working_dir+"/DNNDumper", False) for f in get_dir_files("DNNDumper/", ".py")])
    copy_list.extend([(f, working_dir+"/NASBase", False) for f in get_dir_files("NASBase/", ".py")])
    copy_list.extend([(f, working_dir+"/NASBase/dataset", False) for f in get_dir_files("NASBase/dataset", ".py")])
    #copy_list.extend([(f, working_dir+"/Analyse", False) for f in get_dir_files("Analyse/", ".py")])

    #pprint(copy_list); sys.exit()

    return copy_list




class SSH(object):

    def __init__(self, address, username, password, port=22):
        print ("Connecting to server.")
        self._address = address
        self._username = username
        self._password = password
        self._port = port
        self.sshObj = None
        self.connect()
        self.scp = SCPClient(self.sshObj.get_transport(), progress=self.progress)

    def sendCommand(self, command):
        if(self.sshObj):
            stdin, stdout, stderr = self.sshObj.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata

                    print (str(alldata))
        else:
            print ("Connection not opened.")

    def connect(self):
        try:
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self._address, port=self._port, username=self._username, password=self._password, timeout=20, look_for_keys=False)
            print ('Connected to {} over SSh'.format(self._address))
            time.sleep(3)
            return True
        except Exception as e:
            ssh = None
            print ("Unable to connect to {} over ssh: {}".format(self._address, e))
            time.sleep(3)
            return False
        finally:
            self.sshObj = ssh
    
    def disconnect(self):
        self.scp.close()
        time.sleep(1)
        self.sshObj.close()
        time.sleep(1)


    def progress(self, filename, size, sent):
        perc_complete = float(sent)/float(size)
        if perc_complete == 1:
            sys.stdout.write("%s's progress: %.2f%%   \n" % (filename, float(sent)/float(size)*100) )



def arg_parser():
    setting_selection = {}
    parser = argparse.ArgumentParser('Parser User Input Arguments')
    parser.add_argument('-s', '--server',    type=str, default=argparse.SUPPRESS,  help="server selection")   
    args = parser.parse_args()

    if 'server' in args:
        if args.server in list(GPU_SERVER_SETTINGS.keys()) or args.server == 'all':
            setting_selection['server'] = args.server
        else:
            sys.exit("Server name invalid: options: " + str(list(GPU_SERVER_SETTINGS.keys())))
    else:
        sys.exit("Server not selected")

    return setting_selection




if __name__ == "__main__":
    
    setting_selection = arg_parser()

    server_name = setting_selection['server']

    # Parse and check the arguments    
    if server_name == 'all':    # push code to all GPU servers

        for each_server_name in GPU_SERVER_SETTINGS.keys():
            print ("\n\n====================================================")
            print ("Uploading to : ", each_server_name.upper())
            print ("====================================================")
            server_settings = GPU_SERVER_SETTINGS[each_server_name]
            ssh = SSH(server_settings['REMOTE_IP'], server_settings['REMOTE_USER'], server_settings['REMOTE_PASS'])        

            # copy folders/files
            copy_list = get_copy_list(server_settings['WORKING_DIR'])
            for f, d, r in copy_list:
                print("\n---: ", d, f, "dir_recursive=", r)
                ssh.scp.put(f, remote_path=d, recursive=r)

            ssh.disconnect()
    
    else:
        server_settings = GPU_SERVER_SETTINGS[server_name]
        ssh = SSH(server_settings['REMOTE_IP'], server_settings['REMOTE_USER'], server_settings['REMOTE_PASS'])     

        print ("\n\n====================================================")
        print ("Uploading to : ", server_name.upper())
        print ("====================================================")   

        # copy folders/files
        copy_list = get_copy_list(server_settings['WORKING_DIR'])
        for f, d, r in copy_list:
            print("\n---: ", d, f, "dir_recursive=", r)
            ssh.scp.put(f, remote_path=d, recursive=r)

        ssh.disconnect()
        

