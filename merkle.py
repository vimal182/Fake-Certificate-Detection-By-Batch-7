# blockchain/merkle.py

import hashlib

def hash_pair(a, b):
    return hashlib.sha256((a + b).encode()).hexdigest()

def build_merkle_tree(transactions):
    if not transactions:
        return [], None

    tree = [transactions]
    level = transactions

    while len(level) > 1:
        new_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            new_level.append(hash_pair(left, right))
        tree.append(new_level)
        level = new_level

    return tree, level[0]

def get_merkle_proof(tree, target_hash):
    proof = []
    for level in tree:
        if len(level) == 1:
            break
        if target_hash in level:
            index = level.index(target_hash)
            sibling_index = index ^ 1
            if sibling_index < len(level):
                proof.append(level[sibling_index])
            else:
                proof.append(level[index])
            target_hash = hash_pair(
                level[index] if index % 2 == 0 else level[sibling_index],
                level[sibling_index] if index % 2 == 0 else level[index]
            )
    return proof

def verify_merkle_proof(target_hash, proof, merkle_root):
    computed_hash = target_hash
    for sibling in proof:
        computed_hash = hash_pair(computed_hash, sibling)
    return computed_hash == merkle_root