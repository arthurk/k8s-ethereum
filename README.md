k8s-ethereum
============

Ethereum Nodes in Kubernetes.

Currently supported operations are:

  - Private network
  - Mainnet light client

Support for full nodes is planned.

Properties of the private network:

  - PoA mining with 3s block time
  - 10 initial accounts each funded with 1 million ether
  - Json-rpc enabled (tested with MetaMask and Truffle)

Installation
------------

Requirements:

  - A Kubernetes 1.10 cluster (e.g. minikube) and kubectl configured
  - Python 3.6
  - pipenv

1. Clone this repo
2. Run `pipenv install`

Now either prefix all commands with `pipenv run` or run them within `pipenv shell`.

Usage (Private network)
-----------------------

```bash
# Create network. This will also create 10 initial accounts.
# The --name argument is also the k8s namespace name
$ python main.py --name mynetwork --create
2018-06-10 00:02:42,470 INFO     Creating network "mynetwork"
Address: 0xB6B03E6d12f8AB152fbc1F80C2691d58c2BC607D Private Key: f37fc29fa28bc394d015db7374df941f93f63dc50d52e5bc68f1706a2f546366
...
Address: 0x474B8a1028Abb8883763Ab21C2e4cb47b59367b6 Private Key: 250ad5cb94c902d46f1a18255a8b17f5879a4e1b5b94fcee4e95969b5a05426c
2018-06-10 00:02:44,176 INFO     Network created

# Check pods with kubectl
$ kubectl -n mynetwork get pods
NAME                    READY     STATUS    RESTARTS   AGE
geth-5f8df95b79-xmk45   1/1       Running   0          7h

# Check the pod log. You can also pass `-f` and see the blocks being mined.
$ kubectl -n mynetwork log geth-5f8df95b79-xmk45
INFO [06-09|14:49:34] Maximum peer count                       ETH=25 LES=0 total=25
INFO [06-09|14:49:34] Allocated cache and file handles         database=/opt/geth/geth/chaindata cache=16 handles=16
INFO [06-09|14:49:34] Writing custom genesis block 
...

# Get the network IP from minikube. You can use this in MetaMask, Truffle etc.
$ minikube service geth -n mynetwork --url
http://192.168.64.2:32632

# Attach to geth console
$ geth attach "http://192.168.64.2:32632"
Welcome to the Geth JavaScript console!

instance: Geth/v1.8.10-stable/linux-amd64/go1.10.2
coinbase: 0xb6b03e6d12f8ab152fbc1f80c2691d58c2bc607d
at block: 73 (Sat, 09 Jun 2018 16:53:12 CEST)
 modules: eth:1.0 net:1.0 personal:1.0 rpc:1.0 txpool:1.0 web3:1.0
...

# Delete network
$ python main.py --name mynetwork --delete
```

It's possible to create multiple networks by changing the `name` argument. For example to create 3 private networks run:

```
$ python main.py --name network1 --create
$ python main.py --name network2 --create
$ python main.py --name network3 --create
```

Usage Light Client
------------------

```shell
python main.py --name foo --light --create
python main.py --name foo --light --delete
```

Light sync might take hours. Depending on how many peers are available.

Minikube
--------

If you're running minikube you need to get the geth service ip with:

    minikube service geth --url
