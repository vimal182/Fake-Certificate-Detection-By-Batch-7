# blockchain/block.py

import hashlib
import json
from datetime import datetime


class Block:
    def __init__(self, index, institution_id, transactions, previous_hash):
        self.index = index
        self.timestamp = str(datetime.utcnow())
        self.institution_id = institution_id
        self.transactions = transactions  
        self.merkle_root = None
        self.previous_hash = previous_hash
        self.signature = None
        self.block_hash = None

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "institution_id": self.institution_id,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash
        }

        return hashlib.sha256(
            json.dumps(block_data, sort_keys=True).encode()
        ).hexdigest()

    def to_dict(self):
        return self.__dict__