from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.api import Client
from base58 import b58encode, b58decode

from solders.message import MessageV0
from solders.transaction import VersionedTransaction


SOLANA_RPC_URL_DEVNET = "https://api.devnet.solana.com"
SOLANA_RPC_URL_MAINNET = "https://api.mainnet-beta.solana.com"

SOLANA_RPC_URL = SOLANA_RPC_URL_DEVNET
solana_rpc_mode = "Devnet"
client = Client(SOLANA_RPC_URL)


class SolanaHelper:
    @staticmethod
    def getMode():
        return solana_rpc_mode

    @staticmethod
    def switch_mode(use_mainnet=False):
        global SOLANA_RPC_URL, client, solana_rpc_mode
        SOLANA_RPC_URL = SOLANA_RPC_URL_MAINNET if use_mainnet else SOLANA_RPC_URL_DEVNET
        solana_rpc_mode = "Mainnet" if use_mainnet else "Devnet"
        client = Client(SOLANA_RPC_URL)

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
            lamports = response.value
            sol = lamports / 1_000_000_000
            return sol
        except Exception as e:
            print("Error getting balance:", e)
            return 0.0

    @staticmethod
    def send_sol(from_private_key: str, to_public_key: str, amount_sol: float):
        try:
            print("From Private Key:", from_private_key)
            print("To Public Key:", to_public_key)
            print("Amount:", amount_sol)

            from_keypair = Keypair.from_bytes(b58decode(from_private_key))
            to_pubkey = Pubkey.from_string(to_public_key)
            lamports = int(amount_sol * 1_000_000_000)

            print("Lamports to send:", lamports)

            ix = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports,
                )
            )

            blockhash_resp = client.get_latest_blockhash()
            blockhash = blockhash_resp.value.blockhash

            if not blockhash:
                return {"success": False, "error": "Failed to fetch latest blockhash"}

            # ✅ Use MessageV0 instead of Message
            msg = MessageV0.try_compile(
                payer=from_keypair.pubkey(),
                instructions=[ix],
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash
            )

            txn = VersionedTransaction(msg, [from_keypair])

            print("Transaction Prepared:", txn)

            send_resp = client.send_transaction(txn)

            if send_resp.value:
                return {"success": True, "signature": send_resp.value}
            else:
                return {"success": False, "error": str(send_resp)}

        except Exception as e:
            return {"success": False, "error": str(e)}
