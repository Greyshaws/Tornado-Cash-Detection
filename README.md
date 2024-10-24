# Tornado-Cash-Detection

This script detects money movement coming from Tornado Cash. It accepts an Ethereum block number as input, and prints out the following information for each detected Tornado Cash transfer:
* transaction hash
* funded address
* value of sent ether
  
If no Tornado Cash transfer is detected in the block, it prints out "No Tornado Cash transfer detected."
