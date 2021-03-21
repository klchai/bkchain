# Projet Blockchain
## classes.py
- Transactions: Contient des informations de base sur une transaction, l'acheteur(payer), le vendeur(beneficiary), le montant(amount) et l'horodatage(timestamp)
- Block: Contient l'index du bloc, la difficulté(nonce) et la transaction qui a eu lieu. Les blocs peuvent également être créés à partir d'un hachage (en utilisant un arbre de merekle)
- Blockchain: Contient l'ajout de blocs à la chaîne, l'extraction de blocs(mine) et la vérification de l'intégrité de la blockchain

## wallet.py
- Se connecter à un mineur
- Transactions entre deux portefeuilles
