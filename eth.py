import json
from ecdsa import SigningKey, SECP256k1
import sha3


def checksum_encode(addr_str): # Takes a hex (string) address as input
    keccak = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak.update(addr.encode('ascii'))
    hash_addr = keccak.hexdigest()
    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c
    return '0x' + out

def create_eth_address():
    keccak = sha3.keccak_256()

    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key().to_string()

    keccak.update(pub)
    address = keccak.hexdigest()[24:]

    return {'private_key': priv.to_string().hex(),
            'public_key': pub.hex(),
            'address': checksum_encode(address)}


def get_genesis_content(accounts):
    """
    Create genesis json for geth.

    Accounts will be funded with 1 million ether.
    Accounts[0] is the coinbase/etherbase
    """
    # 1 Million ether
    initial_balance = '0xD3C21BCECCEDA1000000'
    data = {
      "config": {
        "chainId": 1213,
        "clique": {
          "period": 3,
          "epoch": 30000
        }
      },
      "nonce": "0x0",
      "timestamp": "0x5b007880",
      "extraData": "0x0000000000000000000000000000000000000000000000000000000000000000{0}0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000".format(accounts[0]['address'][2:]),
      "gasLimit": "0x5fdfb1",
      "difficulty": "0x1",
      "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
      "coinbase": "0x0000000000000000000000000000000000000000",
      "alloc": {
        accounts[0]['address']: {
          "balance": initial_balance
        }
      }
    }

    # add remaining accounts to alloc
    for account in accounts[1:]:
        data['alloc'][account['address']] = {'balance': initial_balance}

    return json.dumps(data)
