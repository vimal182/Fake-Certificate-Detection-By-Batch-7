# blockchain/chain.py

import json
import os
from datetime import datetime

from .block import Block
from .crypto_utils import (
    sign_data,
    verify_signature,
    load_private_key,
    load_public_key
)
from .merkle import build_merkle_tree

LEDGER_FILE = "blockchain/ledger.json"


class Blockchain:

    def __init__(self):
        os.makedirs("blockchain", exist_ok=True)

        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    
    # Load / Save
    

    def load_chain(self):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)

    def save_chain(self, chain):
        with open(LEDGER_FILE, "w") as f:
            json.dump(chain, f, indent=4)

    
    # Add Certificate Block
    

    def add_certificate_block(self, institution_id, certificate_hashes):

        chain = self.load_chain()
        previous_hash = chain[-1]["block_hash"] if chain else "0"

        transactions = [
            {
                "type": "ISSUE",
                "certificate_hash": h,
                "timestamp": str(datetime.utcnow())
            }
            for h in certificate_hashes
        ]

        hash_list = [tx["certificate_hash"] for tx in transactions]
        tree, merkle_root = build_merkle_tree(hash_list)

        block = Block(
            index=len(chain),
            institution_id=institution_id,
            transactions=transactions,
            previous_hash=previous_hash
        )

        block.merkle_root = merkle_root
        block.block_hash = block.compute_hash()

        private_key = load_private_key(institution_id)
        signature = sign_data(private_key, block.block_hash)
        block.signature = signature.hex()

        chain.append(block.to_dict())
        self.save_chain(chain)

        return block.to_dict()

    
    # Add Revocation Block
   

    def revoke_certificate(self, institution_id, certificate_hash, reason):

        chain = self.load_chain()
        previous_hash = chain[-1]["block_hash"] if chain else "0"

        transaction = {
            "type": "REVOCATION",
            "certificate_hash": certificate_hash,
            "reason": reason,
            "timestamp": str(datetime.utcnow())
        }

        block = Block(
            index=len(chain),
            institution_id=institution_id,
            transactions=[transaction],
            previous_hash=previous_hash
        )

        block.merkle_root = certificate_hash
        block.block_hash = block.compute_hash()

        private_key = load_private_key(institution_id)
        signature = sign_data(private_key, block.block_hash)
        block.signature = signature.hex()

        chain.append(block.to_dict())
        self.save_chain(chain)

        return block.to_dict()

    
    # Check Revocation Status
    

    def is_revoked(self, certificate_hash):
        chain = self.load_chain()

        for block in chain:
            for tx in block["transactions"]:
                if (
                    tx["type"] == "REVOCATION"
                    and tx["certificate_hash"] == certificate_hash
                ):
                    return True, tx["reason"]

        return False, None

    
    # Full Chain Verification
    

    def verify_chain(self):
        chain = self.load_chain()

        for i in range(len(chain)):

            current = chain[i]

            block_obj = Block(
                index=current["index"],
                institution_id=current["institution_id"],
                transactions=current["transactions"],
                previous_hash=current["previous_hash"]
            )

            block_obj.timestamp = current["timestamp"]
            block_obj.merkle_root = current["merkle_root"]

            recalculated_hash = block_obj.compute_hash()

            if recalculated_hash != current["block_hash"]:
                return False

            public_key = load_public_key(current["institution_id"])

            if not verify_signature(
                public_key,
                current["block_hash"],
                bytes.fromhex(current["signature"])
            ):
                return False

            if i > 0:
                if current["previous_hash"] != chain[i - 1]["block_hash"]:
                    return False

        return True