VAGRANTFILE_API_VERSION = "2"
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker' # docker is provider
ENV['FORWARD_DOCKER_PORTS'] = "1" # enable port forwarding

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

BASE_IMAGE  = "./nodes" # use base centos image, install with python
 
NODES = {:nameprefix => "node-",  # prefix for node namesd.image = NODES[:image]
              :subnet => "10.0.1.", # basically IP prefix
              :ip_offset => 100,  # nodes will have IPs like: 10.0.1.101, .102
              :image => BASE_IMAGE, # use base centos img
              :port => 5000 } # port to use

NODES_COUNT = 6 # number of total nodes

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| # vagrant config start

  #config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".*/"
  config.ssh.insert_key = false

  (1..NODES_COUNT).each do |i| # create 1 to N nodes
    node_ip_addr = "#{NODES[:subnet]}#{NODES[:ip_offset] + i}"
    node_name = "#{NODES[:nameprefix]}#{i}"
    config.vm.define node_name do |s| # define one particular node
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.provider "docker" do |d|
        d.build_dir = "./nodes"
        d.name = node_name
        d.has_ssh = true
      end
    end
  end
  
  config.vm.provision :shell, :inline => "python3 /home/main.py #{NODES_COUNT}"
end
# EOF
