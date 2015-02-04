###[Work in progress]

This is a port of YCSB (see full description of YCSB here: https://github.com/brianfrankcooper/YCSB/) which builds on the Thumbtack version to include automating the DB provisioning and installation using EC2.

This version is a prototype, still under development. Windows in not supported as a client OS.

By default it uses AWS's free tier (good for getting going) but it is best to use larger instances for real tests.

As an example (once installed) you could run the following commands to test the throughput limit of say Cassandra for a particular number of VMs:

- fab ec2_up:cassandra           #Provision 2 VMs (hosts defined in fabfile/conf/hosts.py)
- fab db_up:cassandra            #Install cassandra on these VMs
- fab ycsb_deploy                #Deploy YCSB
- fab ycsb_load                  #Use YCSB to load a dataset (defined by paratmeters set in fabfile/conf/workloads.py)
- fab threads_w:cassandra        #Run a workload with an increasing number of threads until throughput saturates

repeat again replacing 'cassandra' with 'mongodb'

Longer more complex experiments are also supported such as increasing the number of nodes incrementally or increasing the amount of data in the database between runs. These can take a long time to run. They automatically produce graphs.

Supported commands:

**EC2**

- ec2_up
- ec2_down
- ec2_status
- db_up
- db_down

**YCSB**

- ycsb_load
- ycsb_run
- ycsb_status
- ycsb_get
- ycsb_deploy
- ycsb_kill
- ycsb_clean
- ycsb_inittables

**Experiments**

- max_load_throughput
- max_workload_throughput
- seq_workloads
- grow_nodes
- grow_data

**Instalation**

 sudo apt-get install fabric
 sudo pip install pytx
 sudo apt-get install python-pandas

sudo pip install awscli

aws configure (add your public/private key and leave the format as 'text')

place your ec2 .pem file in the YCSB directory

alter the file: fabfile/conf/hosts.py
    key_name = keyfile_name_without_dot_pem_at_end
    security_group = yoursecuritygroupname


As a final note, I used Fabric as I wanted to stick with the path already trodden by Thumbtack. If I were to work on this further I would probably not choose that framework. Saltstack or Ansible would be preferable.