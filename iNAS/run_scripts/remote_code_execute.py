
import sys
import time
import getpass
import paramiko


# -- populate as required --
GPU_SERVER_SETTINGS = {   
    
    'gs154' : {
        "REMOTE_IP" : 'xxx.xxx.xxx.xxx', "REMOTE_USER" : 'username', "REMOTE_PASS" : 'password',
        "WORKING_DIR" : "/path/to/working_dir",
    }
    
}

# to be run from WORKING_DIR
BATCH_RUN_CMDS = {
    # -- stop all, clean all --
    # "gs154" : ['\x03', '\x03', "pkill python\n", "./clean_all.sh\n",],   

    # -- CIFAR all runs --    
    # "gs154" : ['\x03', "./clean_all.sh\n", "python -m run_scripts.run_batch_generic --runids 0 1 2 --dataset cifar --powtype INTPOW\n"],
    
}




def exec_cmd(shell, cmd , delay=2):
    shell.send(cmd)
    time.sleep(delay)
    sys.stdout.buffer.write(shell.recv(10000))
    sys.stdout.buffer.flush()
    time.sleep(delay)
    print()



def server_init(ssh, server):
    ssh.connect(GPU_SERVER_SETTINGS[server]['REMOTE_IP'],
            username=GPU_SERVER_SETTINGS[server]['REMOTE_USER'],
            password=GPU_SERVER_SETTINGS[server]['REMOTE_PASS'])
    shell = ssh.invoke_shell()
    shell.settimeout(0.25)
    
    return ssh, shell
    



def run_batch(ssh):
    for server,cmdlst in BATCH_RUN_CMDS.items():
        if cmdlst != []:
            ssh, shell = server_init(ssh, server) # login

            time.sleep(2)
            exec_cmd(shell, 'screen -r eval_auto\n')
            exec_cmd(shell, 'cd ' + GPU_SERVER_SETTINGS[server]['WORKING_DIR'] +' \n')
            exec_cmd(shell, 'ls -l\n')

            # run cmd
            for each_cmd in cmdlst:
                exec_cmd(shell, each_cmd)

            exec_cmd(shell, '\x01\x04')
            exec_cmd(shell, '\x01\x04')
    
            ssh.close()

        


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

run_batch(ssh)

print()


