from web3 import Web3
import requests

RPC_URL = "https://neat-prettiest-haze.quiknode.pro/a7cc6bc914a4c0a6116493c7d194308f973bd763/"
TORNADO_CASH_ADDRESS = "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936".lower() 

# Initialize a connection to the Ethereum node
w3 = Web3(Web3.HTTPProvider(RPC_URL))
print("Connected to Ethereum node")

# Check if connection is successful
if not w3.is_connected():
    print("Failed to connect to the Ethereum node.")
    exit()

# Trace transactions using debug_traceBlockByNumber
def trace_block_by_number(block_number):
    """
    @notice Traces transactions for a given block number.
    @param block_number The block number to trace.
    @return A list of transaction traces or None if an error occurs.
    """
    method = "debug_traceBlockByNumber"
    params = [hex(block_number), {"tracer": "callTracer", "timeout": "10s"}]
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    response = requests.post(RPC_URL, headers={'Content-Type': 'application/json'}, json=payload)
    if response.status_code == 200:
        print(f"Successfully retrieved trace for block {block_number}.")
        return response.json().get("result", [])
    else:
        print(f"Error retrieving traces: {response.status_code}, {response.text}")
        return None

# Recursively trace calls to Tornado Cash contract
def trace_calls_for_tornado(trace, tx_hash):
    """
    @notice Recursively trace internal 'CALL' operations and detect any interaction with Tornado Cash.
    @param trace The trace result from the Ethereum node.
    @param tx_hash The transaction hash of the current trace.
    @return A dictionary containing transaction details if an interaction with Tornado Cash is detected; otherwise, None.
    """
    # Access the result object where the trace data exists
    result = trace.get("result", {})
    
    from_address = result.get("from", "Unknown").lower()
    to_address = result.get("to", "Unknown").lower()
    value_hex = result.get("value", "0x0")
    value = int(value_hex, 16) / 10**18  # Convert from wei to ether

    # Check for Tornado Cash address
    interactions = []
    if from_address == TORNADO_CASH_ADDRESS:
        interactions.append({
            "transaction_hash": tx_hash,
            "to_address": to_address,
            "value": value
        })

    # Trace internal/nested calls
    if "calls" in result:
        for call in result["calls"]:
            interactions.extend(trace_calls_for_tornado({"result": call}, tx_hash))  # Append found interactions

    return interactions  # Return all found interactions

# Detect interactions with Tornado Cash from trace results
def detect_tornado_cash_interactions(trace_result):
    """
    @notice Detects interactions with Tornado Cash.
    @param trace_result The trace results obtained from the Ethereum node.
    @return List of detected interactions with Tornado Cash.
    """
    detected_interactions = []

    # Iterate over traces to find any interactions with Tornado Cash
    for trace in trace_result:
        try:
            tx_hash = trace.get("txHash")  # Get the transaction hash for the current trace
            # Recursively trace all calls and detect interactions
            interactions = trace_calls_for_tornado(trace, tx_hash)
            detected_interactions.extend(interactions)  # Add found interactions to the main list

        except Exception as e:
            print(f"Error processing trace: {e}")
            print("Trace data causing the error:", trace)  # Print trace for further inspection

    return detected_interactions

# Execute the script
def main():
    """
    @notice Main function to execute the script.
    Prompts the user for a block number and displays detected interactions with Tornado Cash.
    @return None
    """
    block_number = int(input("Enter block number: "))

    # Retrieve trace results for the specified block
    trace_result = trace_block_by_number(block_number)

    if trace_result is not None:
        print(f"Detecting interactions with Tornado Cash for block number: {block_number}")
        interactions = detect_tornado_cash_interactions(trace_result)

        # Display detected interactions
        if interactions:
            print("\nDetected Interactions with Tornado Cash:")
            for interaction in interactions:
                print(f"Transaction Hash: {interaction['transaction_hash']}")
                print(f"Funded Address: {interaction['to_address']}")
                print(f"Value of sent ether: {interaction['value']} ETH")
                print()
        else:
            print("No interactions with Tornado Cash detected.")
    else:
        print("No trace results returned.")

if __name__ == "__main__":
    main()
