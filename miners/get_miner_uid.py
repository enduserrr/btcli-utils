# Fetch your miner uid
import bittensor as bt

WALLET_NAME = "name"	# Your wallet name
HOTKEY = "name"		# Your hotkey name
NETUID = 1		# Number of the subnet you're mining

subtensor = bt.subtensor(network="finney")
wallet = bt.wallet(name=WALLET_NAME, hotkey=HOTKEY)
hotkey_ss58 = wallet.hotkey.ss58_address

uid = subtensor.get_uid_for_hotkey_on_subnet(hotkey_ss58, NETUID)
print(f"Your UID: {uid}")
