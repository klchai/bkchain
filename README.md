# Projet Blockchain
## Fichier classes.py
Contient les différentes classes utilisées :
- Miner: Représente un mineur
- Transaction: Représente une transaction
- Block: Représente un block de la blockchain
- Blockchain: Représente la blockchain

## Fichier miner.py
Lance un mineur qui tourne sur un port
```console
Usage : python3 miner.py miner_port [other_miner_port]
Description des arguments :
miner_port = port sur lequel tourne le mineur
other_miner_port (facultatif) = port d'un mineur existant sur lequel on va se connecter
```

## Fichier wallet.py
Lance un wallet qui se connecte à un mineur
```console
Usage : python3 wallet.py miner_port
Description des arguments :
miner_port = port d'un mineur existant sur lequel on va se connecter
```
