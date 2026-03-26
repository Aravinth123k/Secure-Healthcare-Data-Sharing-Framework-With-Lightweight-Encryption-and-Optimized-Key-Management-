import hashlib
import time


def create_block(chain, data_hash):
    previous_hash = chain[-1]["block_hash"] if chain else "0"

    block = {
        "index": len(chain) + 1,
        "timestamp": time.time(),
        "data_hash": data_hash,
        "previous_hash": previous_hash,
    }

    block_string = f"{block['index']}{block['timestamp']}{block['data_hash']}{block['previous_hash']}"

    block["block_hash"] = hashlib.sha256(
        block_string.encode()
    ).hexdigest()

    return block
