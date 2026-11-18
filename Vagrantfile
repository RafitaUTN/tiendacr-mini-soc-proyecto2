# frozen_string_literal: true

Vagrant.configure("2") do |config|
  config.vm.box_check_update = false
  config.vm.boot_timeout = 600
  config.ssh.insert_key = true

  machines = {
    "attacker" => {
      box: "kalilinux/rolling",
      version: "2026.2.0",
      vm_name: "Kali-Linux-Atacante",
      hostname: "kali-linux-atacante",
      ip: "10.10.10.30",
      ssh_port: 2201,
      memory: 2048,
      cpus: 2,
      provision: "provisioning/attacker/base.sh"
    },
    "target" => {
      box: "ubuntu/jammy64",
      version: "20241002.0.0",
      vm_name: "Ubuntu-Servidor-Objetivo",
      hostname: "ubuntu-servidor-objetivo",
      ip: "10.10.10.10",
      ssh_port: 2202,
      memory: 2048,
      cpus: 2,
      provision: "provisioning/target/base.sh"
    },
    "siem" => {
      box: "bento/ubuntu-24.04",
      version: "202510.26.0",
      vm_name: "Ubuntu-Servidor-SIEM",
      hostname: "ubuntu-servidor-siem",
      ip: "10.10.10.20",
      ssh_port: 2203,
      memory: 6144,
      cpus: 4,
      provision: "provisioning/siem/base.sh"
    }
  }

  machines.each do |name, machine|
    config.vm.define name do |node|
      node.vm.box = machine[:box]
      node.vm.box_version = machine[:version]
      node.vm.hostname = machine[:hostname]
      node.vm.network "forwarded_port",
        guest: 22,
        host: machine[:ssh_port],
        host_ip: "127.0.0.1",
        id: "ssh",
        auto_correct: false
      node.vm.network "private_network",
        ip: machine[:ip],
        virtualbox__intnet: "tiendacr-lab"

      node.vm.provider "virtualbox" do |vb|
        vb.name = machine[:vm_name]
        vb.memory = machine[:memory]
        vb.cpus = machine[:cpus]
        vb.customize ["modifyvm", :id, "--groups", "/TiendaCR"]
      end

      node.vm.provision "shell",
        path: "provisioning/common/base.sh",
        args: [machine[:hostname]]
      node.vm.provision "shell", path: machine[:provision]
    end
  end
end
