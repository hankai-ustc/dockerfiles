import subprocess
import sys
from argparse import ArgumentParser
import docker
def exec_cmd(cmd,timeout=5):
    output = subprocess.check_output(cmd,stderr=subprocess.STDOUT).strip()
    return output


def create_veth_pair(iface1,iface2):
    cmd = ["ip","link","add",iface1,"type","veth","peer","name",iface2]
    exec_cmd(cmd)

def get_docker_nspid(container_name):
    cmd = ["docker","inspect","-f","{{.State.Pid}}",container_name]
    nspid = exec_cmd(cmd).split('\n')[0]
    return nspid

def add_iface_to_container(container_name,iface1,iface2):
    nspid = get_docker_nspid(container_name)
    subcmd1="/proc/%s/ns/net" %nspid
    subcmd2="/var/run/netns/%s" %nspid
    #exec_cmd(["ln","-s",subcmd1,subcmd2])
    subprocess.Popen(['ln','-s',subcmd1,subcmd2])
    exec_cmd(["ip","link","set","dev",iface1,"name",iface2,"netns",nspid])
    exec_cmd(["ip","netns","exec",nspid,"ip","link","set","dev",iface2,"up"])

if __name__=="__main__":
    create_veth_pair("tt1","tt2")
    create_veth_pair("tt3","tt4")
    exec_cmd(["docker","run","-itd","--rm","--name=test1","--privileged","-v","/home/hankai/Dockerfiles/base/start:/usr/local/bin/start","base"])
    add_iface_to_container("test1","tt2","eth1")
    add_iface_to_container("test1","tt4","eth2")
    

