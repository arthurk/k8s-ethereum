#!/bin/sh
set -ex
ETHSTATS_SECRET=$(cat /opt/ethstats/secret/password)
geth --datadir /opt/geth init /opt/geth/config/genesis.json
geth --datadir /opt/geth account import /opt/geth/secret/private_key --password /opt/geth/secret/password
geth --datadir /opt/geth --networkid=1213 --unlock `cat /opt/geth/secret/address` --password /opt/geth/secret/password --mine --nousb --nodiscover --maxpeers 0 --rpc --rpcaddr 0.0.0.0 --rpcapi=db,eth,net,web3,personal,txpool --rpccorsdomain="*" --rpcvhosts="*" --ethstats=${HOSTNAME}:${ETHSTATS_SECRET}@ethstats
