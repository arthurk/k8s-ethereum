k8s-ethereum
============

Private Ethereum nodes in Kubernetes.

  - PoA mining with 3s block time
  - 3 initial accounts each funded with 1 million ether
  - Json-rpc enabled (tested with MetaMask and Truffle)

Installation
------------

Requirements:

  - Rancher / k3s cluster
  - Python 3.6
  - pipenv
  - kubectl
  - kustomize

1. Clone this repo
2. Run `./create_site.bash`
3. Run `kustomize build . | kubectl apply -f -`

