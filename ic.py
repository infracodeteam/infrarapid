#!/usr/bin/env python3

import argparse
import json
import os
import yaml
from jinja2 import FileSystemLoader, Environment

from library import utils

env = Environment(loader=FileSystemLoader('templates'))
SERVICES = {
    'http': ('80', 'tcp'),
    'https': ('443', 'tcp'),
    'ping': ('-1', 'icmp'),
    'ssh': ('22', 'tcp'),
}
PORT2PROTOCOL = {
    '80': 'http',
    '443': 'https'
}


def load_config(config):
    content = yaml.safe_load(config)
    return content


def initialize_directories(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            print("Creating directories for templates failed!")
            raise e


def port2protocol(port):
    port = str(port)
    if port not in PORT2PROTOCOL:
        return 'tcp'
    return PORT2PROTOCOL[port]


class ParseConfig:

    def __init__(self, data):
        self.networks = []
        self.data = data

    def run(self):
        servers = []
        provider = {}
        provider['lb'] = []
        provider['region'] = self.data['region']
        provider['vpc_network'] = self.data['vpc_network']
        provider['ssh_key_path'] = self.data['ssh_key_path']
        data_servers = self.data.get('servers', [])
        lbs = self.data.get('load_balancers', [])
        subnets_servers = [s['network'] for s in data_servers]
        provider['public_subnets'] = json.dumps(list({
            s['network'] for s in data_servers
            if bool(s['external_access'])}))

        server_lbs = {}
        for lb in lbs:
            listeners = []
            health_check = []
            for lis in lb['listeners']:
                inst_port, lb_port = list(lis.items())[0]
                listener = {
                    'instance_port': inst_port,
                    'instance_protocol': port2protocol(inst_port),
                    'lb_port': lb_port,
                    'lb_protocol': port2protocol(lb_port),
                }
                listeners.append(listener)
            if 'health' in lb:
                hch = lb['health']
                h_check = hch['protocol'] + ":" + hch['port'] + hch['path']
                health_check.append(h_check)
            lb = {
                'name': lb['name'],
                'listeners': listeners,
                'health_check': health_check,
            }
            server_lbs[lb['name']] = lb

        for s in data_servers:
            server = {}
            server['name'] = s['server']
            server['count'] = s['count']
            server['instance_type'] = s['size']
            server['os'] = s['os']
            if 'remote_command' in s:
                server['remote_command'] = json.dumps(s['remote_command'])
            if 'local_command' in s:
                server['local_command'] = s['local_command']
            subnet_index = subnets_servers.index(s['network'])
            server['subnet'] = "public-subnet[%d]" % subnet_index
            if 'external_access' in s:
                ports = [SERVICES[p]
                         for p in s['external_access'] if p in SERVICES]
                ports += [p.split("/")
                          for p in s['external_access'] if p not in SERVICES]
                server['security_groups'] = [
                    {
                        'from_port': p[0],
                        'to_port': p[0],
                        'protocol': p[1],
                        'cidr_blocks': ['0.0.0.0/0']
                    }
                    for p in ports]
            if 'tags' in s:
                server['tags'] = utils.dict2hcl(
                    s['tags'], tabs=8, only_values=True)
            if 'load_balancer' in s:
                lb = server_lbs[s['load_balancer']]
                lb['server'] = server['name']
                provider['lb'].append(lb)
            servers.append(server)
        return {'servers': servers, 'provider': provider}


class CloudGen:
    prefix = None

    def __init__(self, data):
        self.cloud = data
        self.parsed = ParseConfig(self.cloud).run()

    def generate(self, path):
        for text, filename in (
                (self.generate_vars(), "vars.tf"),
                (self.generate_var_values(), "terraform.tfvars"),
                (self.generate_templates(), "main.tf")
        ):
            with open(os.path.join(path, filename), "w") as f:
                f.write(text)

    def generate_text(self):
        tf_vars = self.generate_vars()
        values = self.generate_var_values()
        templates = self.generate_templates()
        return {
            "vars.tf": tf_vars,
            "terraform.tfvars": values,
            "main.tf": templates
        }

    def generate_vars(self):
        template = env.get_template(os.path.join(self.prefix, 'vars.tf.j2'))
        text = template.render(data=self.parsed)
        return text

    def generate_var_values(self):
        template = env.get_template(os.path.join(self.prefix,
                                                 'terraform.tfvars.j2'))
        text = template.render(data=self.parsed)
        return text

    def generate_templates(self):
        template = env.get_template(os.path.join(self.prefix, 'main.tf.j2'))
        text = template.render(data=self.parsed)
        return text


class AwsLite(CloudGen):

    def __init__(self, data):
        super().__init__(data)
        self.prefix = "aws"


class AzureLite(CloudGen):

    def __init__(self, data):
        super().__init__(data)
        self.prefix = "azure"


class TopologyObject:
    def __init__(self, data, azure=True, aws=True):
        self.data = data
        self.azure = azure
        self.aws = aws
        if azure:
            self.az = AzureLite(self.data)
        if aws:
            self.aw = AwsLite(self.data)

    def generate_templates(self):
        result = {}
        if self.azure:
            result['azure'] = self.az.generate_text()
        if self.aws:
            result['aws'] = self.aw.generate_text()
        return result


def main():
    parser = argparse.ArgumentParser(description='InfraCode')
    parser.add_argument('-c', '--config-file', required=True,
                        type=argparse.FileType('r'),
                        help='Path to configuration file')
    parser.add_argument('-t', '--templates-path', default=".", type=str,
                        help="Path to generated templates")
    args = parser.parse_args()
    initialize_directories(args.templates_path)
    clouds = load_config(args.config_file)['clouds']

    for cloud in clouds:
        if cloud == 'aws':
            aws = AwsLite(clouds[cloud])
            aws.generate(args.templates_path)
        if cloud == 'azure':
            azure = AzureLite(clouds[cloud])
            azure.generate(args.templates_path)


if __name__ == '__main__':
    main()
