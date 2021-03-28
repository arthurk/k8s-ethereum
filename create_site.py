import json
import random
import os
import string

from eth import create_eth_address, get_genesis_content


def pwgen():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def create_accounts(num=3):
    accounts = []
    for i in range(num):
        account = create_eth_address()
        accounts.append(account)
    return accounts


def create_genesis(accounts):
    return get_genesis_content(accounts)


def main():
    os.umask(0o077)
    os.chdir(os.path.dirname('./' + __file__))
    if os.path.exists('./site/genesis.json'):
        print('genesis.json already created')
        return

    # Create accounts
    accounts = create_accounts()
    for i, a in enumerate(accounts):
        os.makedirs('./site/secrets/account/{}'.format(i), 0o700, exist_ok=True)
        with open('./site/secrets/account/{}/address'.format(i), 'w') as f:
            f.write(a['address'])
        with open('./site/secrets/account/{}/private_key'.format(i), 'w') as f:
            f.write(a['private_key'])
        with open('./site/secrets/account/{}/password'.format(i), 'w') as f:
            f.write(pwgen())
        print('created account {}'.format(i))

    # Create ethstats password
    os.makedirs('site/secrets/ethstats', exist_ok=True)
    with open('./site/secrets/ethstats/password', 'w') as f:
        f.write(pwgen())

    # Create genesis
    os.makedirs('site', exist_ok=True)
    genesis_json = create_genesis(accounts)
    with open('./site/genesis.json', 'w') as f:
        f.write(genesis_json)
    print('created genesis.json')

    # Create site kustomization
    kustom = {
        'apiVersion': 'kustomize.config.k8s.io/v1beta1',
        'kind': 'Kustomization',
        'configMapGenerator': [{
            'name': 'geth-config',
            'files': ['genesis.json'],
            'options': {
                'disableNameSuffixHash': True,
            }
        }],
        'secretGenerator': [{
            'name': 'geth-secret',
            'files': [
                './secrets/account/0/address',
                './secrets/account/0/private_key',
                './secrets/account/0/password',
            ],
            'options': {
                'disableNameSuffixHash': True,
            }
        }, {
            'name': 'ethstats-secret',
            'files': [
                './secrets/ethstats/password',
            ],
            'options': {
                'disableNameSuffixHash': True,
            }
        }],
    }
    with open('./site/kustomization.yaml', 'w') as f:
        json.dump(kustom, f)
    print('created kustomization.yaml')


if __name__ == '__main__':
    main()
