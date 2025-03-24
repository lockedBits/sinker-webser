from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.api import Client
from base58 import b58encode, b58decode

SOLANA_RPC_URL_DEVNET = "https://api.devnet.solana.com"
SOLANA_RPC_URL_MAINNET = "https://api.mainnet-beta.solana.com"

SOLANA_RPC_URL = SOLANA_RPC_URL_DEVNET
SOLANA_RPC_MODE = "Devnet"


client = Client(SOLANA_RPC_URL)


class SolanaHelper:


    @staticmethod
    def getMode():
        return {
            SOLANA_RPC_MODE
        }
    
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
            pubkey = Pubkey.from_string(public_key_str)
            response = client.get_balance(pubkey)

            # Properly access the lamports
            lamports = response.value  # This works with solana-py client
            sol = lamports / 1_000_000_000
            return sol
        except Exception as e:
            print("Error getting balance:", e)
            return 0.0

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
                    lamports=lamports,
                )
            )

            blockhash_resp = client.get_latest_blockhash()
            blockhash = blockhash_resp.value.blockhash  # Correct way to access it

            msg = Message(instructions=[ix], payer=from_keypair.pubkey(), recent_blockhash=blockhash)
            txn = Transaction(msg, [from_keypair])
            send_resp = client.send_transaction(txn)

            return {"success": True, "signature": send_resp.value}
        except Exception as e:
            return {"success": False, "error": str(e)}
