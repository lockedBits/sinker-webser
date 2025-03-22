from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import Transaction
from solders.instruction import Instruction
from solders.message import Message
from solders.system_program import transfer, TransferParams
from solana.rpc.api import Client
from base58 import b58encode, b58decode

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
    def get_balance(public_key: str):
        try:
            response = client.get_balance(Pubkey.from_string(public_key))
            if "result" in response and response["result"]:
                lamports = response["result"]["value"]
                return {"success": True, "balance_sol": lamports / 1_000_000_000}
            return {"success": False, "error": "No result in response"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_sol(from_private_key: str, to_public_key: str, amount_sol: float):
        try:
            from_keypair = Keypair.from_bytes(b58decode(from_private_key))
            to_pubkey = Pubkey.from_string(to_public_key)
            lamports = int(amount_sol * 1_000_000_000)

            ix = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )

            blockhash = client.get_latest_blockhash()["result"]["value"]["blockhash"]
            msg = Message([ix], payer=from_keypair.pubkey(), recent_blockhash=blockhash)
            txn = Transaction(msg, [from_keypair])
            txn_sig = client.send_transaction(txn)["result"]

            return {"success": True, "signature": txn_sig}
        except Exception as e:
            return {"success": False, "error": str(e)}
