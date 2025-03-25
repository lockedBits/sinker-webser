from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solders.rpc.api import Client
from base58 import b58encode, b58decode

# Solana RPC Endpoints
SOLANA_RPC_URL_DEVNET = "https://api.devnet.solana.com"
SOLANA_RPC_URL_MAINNET = "https://api.mainnet-beta.solana.com"

# Use Devnet by default
SOLANA_RPC_URL = SOLANA_RPC_URL_DEVNET
solana_rpc_mode = "Devnet"
client = Client(SOLANA_RPC_URL)


class SolanaHelper:
    @staticmethod
    def getMode():
        return solana_rpc_mode

    @staticmethod
    def switch_mode(use_mainnet=False):
        """Switch between Devnet and Mainnet RPC endpoints."""
        global SOLANA_RPC_URL, client, solana_rpc_mode
        SOLANA_RPC_URL = SOLANA_RPC_URL_MAINNET if use_mainnet else SOLANA_RPC_URL_DEVNET
        solana_rpc_mode = "Mainnet" if use_mainnet else "Devnet"
        client = Client(SOLANA_RPC_URL)  # Reinitialize client

    @staticmethod
    def generate_wallet():
        """Generate a new Solana wallet (private & public keys)."""
        keypair = Keypair()
        private_key = b58encode(bytes(keypair)).decode()
        public_key = str(keypair.pubkey())
        return {
            "private_key": private_key,
            "public_key": public_key
        }

    @staticmethod
    def get_balance(public_key_str: str):
        """Retrieve SOL balance for a given public key."""
        try:
            pubkey = Pubkey.from_string(public_key_str)
            response = client.get_balance(pubkey)

            if not response or response.value is None:
                return {"success": False, "error": "Failed to fetch balance"}

            sol_balance = response.value / 1_000_000_000
            return {"success": True, "balance": sol_balance}

        except Exception as e:
            return {"success": False, "error": f"Balance check failed: {str(e)}"}

    @staticmethod
    def send_sol(from_private_key: str, to_public_key: str, amount_sol: float):
        """Send SOL from one wallet to another."""
        try:
            # ✅ Validate inputs
            if not from_private_key or not to_public_key:
                return {"success": False, "error": "Invalid sender or recipient key"}
            if amount_sol <= 0:
                return {"success": False, "error": "Amount must be greater than 0 SOL"}

            from_keypair = Keypair.from_bytes(b58decode(from_private_key))
            to_pubkey = Pubkey.from_string(to_public_key)
            lamports = int(amount_sol * 1_000_000_000)  # Convert SOL to lamports

            # ✅ Fetch latest blockhash with error handling
            blockhash_resp = client.get_latest_blockhash()
            if not blockhash_resp or not blockhash_resp.value:
                return {"success": False, "error": "Failed to fetch blockhash"}

            blockhash = blockhash_resp.value.blockhash

            # ✅ Create transfer instruction
            ix = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports,
                )
            )

            # ✅ Create transaction message
            msg = MessageV0.try_compile(
                payer=from_keypair.pubkey(),
                instructions=[ix],
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash,
            )

            # ✅ Sign and send transaction
            txn = VersionedTransaction(msg, [from_keypair])
            send_resp = client.send_transaction(txn)

            if send_resp.value:
                return {"success": True, "signature": send_resp.value}
            else:
                return {"success": False, "error": "Transaction failed"}

        except Exception as e:
            return {"success": False, "error": f"Transaction error: {str(e)}"}
