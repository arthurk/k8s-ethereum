import pathlib
import yaml
import random
import string
import base64
import argparse
import logging

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from eth import create_eth_address, get_genesis_content

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

encode = lambda s: base64.b64encode(str.encode(s)).decode()

config.load_kube_config()


class PrivateNetwork:
    """
    Private Ethereum Network (using geth)
    """
    def __init__(self, name):
        self.name = name
        self.namespace = name
        self.accounts = []

    def create_accounts(self, num=10):
        for i in range(num):
            account = create_eth_address()
            self.accounts.append(account)

    def create_namespace(self):
        path = pathlib.Path('k8s/namespace.yaml')
        with path.open() as f:
            body = yaml.load(f)

        body['metadata']['name'] = self.name

        api_instance = client.CoreV1Api()
        api_instance.create_namespace(body)

        logger.debug(f'Created namespace "{self.name}"')

    def delete_namespace(self):
        v1 = client.CoreV1Api()
        try:
            v1.delete_namespace(name=self.name, body=client.V1DeleteOptions())
        except ApiException as e:
            if e.status == 404:
                # don't throw if namespace doesn't exist
                return
            else:
                raise
        logger.debug(f'Deleted namespace "{self.name}"')

    def create_configmap(self):
        genesis = get_genesis_content(self.accounts)

        path = pathlib.Path('k8s/configmap.yaml')
        with path.open() as f:
            body = yaml.load(f)
            body['data']['genesis.json'] = genesis

        api_instance = client.CoreV1Api()
        api_instance.create_namespaced_config_map(self.namespace, body)

        logger.debug('Created ConfigMap')

    def create_secret(self, account):
        path = pathlib.Path('k8s/secret.yaml')
        with path.open() as f:
            body = yaml.load(f)

        password = ''.join(random.choices(string.ascii_letters + string.digits,
                                          k=10))

        body['data']['address'] = encode(account['address'])
        body['data']['private_key'] = encode(account['private_key'])
        body['data']['password'] = encode(password)

        api_instance = client.CoreV1Api()
        api_instance.create_namespaced_secret(self.namespace, body)

        logger.debug('Created Secret')

    def create_service(self):
        path = pathlib.Path('k8s/service.yaml')
        with path.open() as f:
            body = yaml.load(f)

        api_instance = client.CoreV1Api()
        api_instance.create_namespaced_service(self.namespace, body)

        logger.debug('Created Service')

    def create_deployment(self):
        path = pathlib.Path('k8s/deployment.yaml')
        with path.open() as f:
            body = yaml.load(f)

        api_instance = client.AppsV1Api()
        api_instance.create_namespaced_deployment(self.namespace, body)

        logger.debug('Created Deployment')

    def delete(self):
        # this will delete all objects under the namespace
        self.delete_namespace()

    def create(self):
        self.create_accounts()
        # print address and private key
        for account in self.accounts:
            print('Address:', account['address'],
                  'Private Key:', account['private_key'])
        self.create_namespace()
        self.create_secret(self.accounts[0])
        self.create_configmap()
        self.create_service()
        self.create_deployment()


def main():
    # cli args
    parser = argparse.ArgumentParser(description='k8s ethereum private network')
    parser.add_argument('--name', dest='name', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--create', dest='create', action='store_true', default=False)
    group.add_argument('--delete', dest='delete', action='store_true', default=False)
    args = parser.parse_args()

    n = PrivateNetwork(args.name)
    if args.create:
        logger.info(f'Creating network "{args.name}"')
        n.create()
        logger.info('Network created')
    elif args.delete:
        logger.info(f'Deleting network "{args.name}"')
        n.delete()
        logger.info('Network deleted')


if __name__ == '__main__':
    main()
