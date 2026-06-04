import json
import pyarrow as pa
from hierachain.core.block import Block
from hierachain.sdk.client import HieraChainClient, HieraChainClientConfig

def main():
    client = HieraChainClient(HieraChainClientConfig('http://localhost:2661'))
    
    # 1. Fetch block 1 from the node API (which reads events from the tampered sqlite db)
    block_data = client.get_block('course_certificates', 1)
    
    # 2. Extract stored block details
    stored_hash = block_data['hash']
    events = block_data['events']
    
    print(f"Stored block hash: {stored_hash}")
    
    # 3. Reconstruct PyArrow Table of events as the node would do
    # Convert list of events to Arrow table
    event_dicts = []
    for e in events:
        event_dict = {
            'entity_id': e['entity_id'],
            'event': e['event'],
            'timestamp': e['timestamp'],
            'data': json.dumps(e.get('details', {})),
            'sender_id': e.get('sender', '')
        }
        event_dicts.append(event_dict)
        
    arrow_table = pa.Table.from_pylist(event_dicts)
    
    # 4. Instantiate a new core Block object using the current (tampered) events
    reconstructed_block = Block(
        index=block_data['index'],
        previous_hash=block_data['previous_hash'],
        timestamp=block_data['timestamp'],
        events=arrow_table,
        creator_id="default-node"  # HieraChain default
    )
    
    recalculated_merkle = reconstructed_block.calculate_merkle_root()
    recalculated_hash = reconstructed_block.calculate_hash()
    
    print(f"Recalculated block hash: {recalculated_hash}")
    
    # 5. Check if the block has been tampered with!
    if stored_hash != recalculated_hash:
        print("\n[CRITICAL ALERT] TAMPERING DETECTED!")
        print("Reason: The recalculated block hash based on the current database events does NOT match the signed block hash stored in the ledger header.")
        print(f"Stored Hash:      {stored_hash}")
        print(f"Recalculated:     {recalculated_hash}")
    else:
        print("\n[SUCCESS] No tampering detected.")

if __name__ == "__main__":
    main()
