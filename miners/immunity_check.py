# Check if your still have immunity as a miner
# (i.e. your miner can't be deregistered => time to set up the miner with no pressure to get emissions)

import bittensor as bt

WALLET_NAME = "name"    # Your wallet name
HOTKEY = "name"         # Your hotkey name
NETUID = 1              # Number of the subnet you're mining

subtensor = bt.subtensor(network="finney")
metagraph = bt.metagraph(netuid=NETUID, network="finney")  # Add this line

wallet = bt.wallet(name=WALLET_NAME, hotkey=HOTKEY)
hotkey_ss58 = wallet.hotkey.ss58_address

uid = subtensor.get_uid_for_hotkey_on_subnet(hotkey_ss58, NETUID)
if uid is None:
    print("Not registered.")
else:
    hp = subtensor.get_subnet_hyperparameters(NETUID)
    immunity_period = hp.immunity_period
    last_update = metagraph.last_update[uid]  # Change to this
    current_block = subtensor.get_current_block()
    blocks_remaining = immunity_period - (current_block - last_update)
    if blocks_remaining > 0:
        print(f"Still immune for ~{blocks_remaining} blocks (~{blocks_remaining * 12 / 3600:.1f} hours).")
    else:
        print("Immunity period ended.")
