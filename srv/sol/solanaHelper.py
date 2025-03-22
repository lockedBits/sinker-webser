from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from base58 import b58encode, b58decode

# Connect to devnet for testing (can be changed to mainnet later)
SOLANA_RPC_URL = "https://api.devnet.solana.com"
solana_client = Client(SOLANA_RPC_URL)


class SolanaHelper:
    @staticmethod
    def generate_wallet():
        keypair = Keypair()
        private_key = b58encode(keypair.secret_key).decode()
        public_key = str(keypair.public_key)
        return {
            "private_key": private_key,
            "public_key": public_key
        }

    @staticmethod
    def get_balance(public_key: str):
        try:
            response = solana_client.get_balance(PublicKey(public_key))
            if response["result"]:
                lamports = response["result"]["value"]
                sol = lamports / 1_000_000_000
                return {"success": True, "balance_sol": sol}
            return {"success": False, "error": "No result in response"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_sol(from_private_key: str, to_public_key: str, amount_sol: float):
        try:
            from_keypair = Keypair.from_secret_key(b58decode(from_private_key))
            to_pubkey = PublicKey(to_public_key)
            lamports = int(amount_sol * 1_000_000_000)

            txn = Transaction()
            txn.add(
                transfer(
                    TransferParams(
                        from_pubkey=from_keypair.public_key,
                        to_pubkey=to_pubkey,
                        lamports=lamports
                    )
                )
            )

            response = solana_client.send_transaction(txn, from_keypair)
            return {"success": True, "signature": response["result"]}
        except Exception as e:
            return {"success": False, "error": str(e)}
