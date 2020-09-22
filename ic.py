#!/usr/bin/env python3

import argparse
import json
import os
import yaml
from jinja2 import FileSystemLoader, Environment

env = Environment(loader=FileSystemLoader('templates'))
SERVICES = {
    'http': ('80', 'tcp'),
    'https': ('443', 'tcp'),
    'ping': ('-1', 'icmp'),
    'ssh': ('22', 'tcp'),
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


class ParseConfig:

    def __init__(self, data):
        self.networks = []
        self.data = data

    def run(self):
        servers = []
        provider = {}
        provider['region'] = self.data['region']
        provider['vpc_network'] = self.data['vpc_network']
        provider['ssh_key_path'] = self.data['ssh_key_path']
        subnets_servers = [s['network'] for s in self.data['servers']]
        provider['public_subnets'] = json.dumps(list({
            s['network'] for s in self.data['servers']
            if bool(s['external_access'])}))

        for s in self.data['servers']:
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
                        'cidr_blocks': json.dumps(['0.0.0.0/0'])
                    }
                    for p in ports]
            servers.append(server)
        return {'servers': servers, 'provider': provider}


class AwsLite:

    def __init__(self, data):
        self.cloud = data
        self.parsed = ParseConfig(self.cloud).run()

    def generate(self, path):
        self.generate_vars(path)
        self.generate_var_values(path)
        self.generate_templates(path)

    def generate_vars(self, path):
        template = env.get_template('vars.tf.j2')
        with open(os.path.join(path, "vars.tf"), "w") as f:
            f.write(template.render(data=self.parsed))

    def generate_var_values(self, path):
        template = env.get_template('terraform.tfvars.j2')
        with open(os.path.join(path, "terraform.tfvars"), "w") as f:
            f.write(template.render(data=self.parsed))

    def generate_templates(self, path):
        template = env.get_template('main.tf.j2')
        with open(os.path.join(path, "main.tf"), "w") as f:
            f.write(template.render(data=self.parsed))


parser = argparse.ArgumentParser(description='InfraCode')
parser.add_argument('-c', '--config-file', required=True,
                    type=argparse.FileType('r'),
                    help='Path to configuration file',)
parser.add_argument('-t', '--templates-path', default=".", type=str,
                    help="Path to generated templates")
args = parser.parse_args()
initialize_directories(args.templates_path)
clouds = load_config(args.config_file)['clouds']

for cloud in clouds:
    if cloud == 'aws':
        aws = AwsLite(clouds[cloud])
        aws.generate(args.templates_path)
