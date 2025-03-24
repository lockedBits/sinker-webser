from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.message import Message
from solders.transaction import Transaction
from base58 import b58encode, b58decode
from solana.rpc.api import Client

SOLANA_RPC_URL = "https://api.devnet.solana.com"
client = Client(SOLANA_RPC_URL)

class SolanaHelper:

    @staticmethod
    def generate_wallet():
        keypair = Keypair()
        private_key = b58encode(bytes(keypair)).decode()
        public_key = str(keypair.pubkey())
        return {
            "private_key": private_key,
            "public_key": public_key
        }

    @staticmethod
    def get_balance(public_key_str: str):
        try:
            public_key = Pubkey.from_string(public_key_str)
            response = client.get_balance(public_key)
            lamports = response["result"]["value"]
            return lamports / 1_000_000_000
        except Exception as e:
            print("Error getting balance:", e)
            return 0.0

    @staticmethod
    def send_sol(from_private_key_b58: str, to_public_key_str: str, amount_sol: float):
        try:
            from_keypair = Keypair.from_bytes(b58decode(from_private_key_b58))
            to_pubkey = Pubkey.from_string(to_public_key_str)
            lamports = int(amount_sol * 1_000_000_000)

            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )

            blockhash = client.get_latest_blockhash()["result"]["value"]["blockhash"]
            message = Message([transfer_ix], payer=from_keypair.pubkey(), recent_blockhash=blockhash)
            txn = Transaction(message, [from_keypair])
            send_resp = client.send_transaction(txn)

            return {
                "success": True,
                "signature": send_resp["result"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
