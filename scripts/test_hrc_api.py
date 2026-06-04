import sys
import logging
from hierachain.sdk.client import HieraChainClient, HieraChainClientConfig, HieraChainAPIError

logging.basicConfig(level=logging.INFO)

def main():
    host = "localhost"
    port = "2661"
    base_url = f"http://{host}:{port}"
    
    client_config = HieraChainClientConfig(
        base_url=base_url,
        timeout=10.0,
        max_retries=1  # Minimize wait time for this test
    )
    client = HieraChainClient(client_config)
    
    chain_name = "course_certificates"
    print("Testing duplicate chain creation:")
    try:
        res = client._request("POST", f"/api/v1/chains/{chain_name}/create", params={"chain_type": "certificate"})
        print("Success! Response:", res)
    except Exception as e:
        print("Failed to create sub-chain:", type(e), e)

if __name__ == "__main__":
    main()
