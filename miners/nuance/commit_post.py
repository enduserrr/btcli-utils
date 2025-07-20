account = "account name"
post_id = "post you replied to"
interaction_id = "your post"
verification_post_id = "my verification post id"
account_id = "x account id(goole)"


import aiohttp
import asyncio
import json
import time
from hashlib import sha256
from uuid import uuid4
from math import ceil
from typing import Any, Optional

import bittensor as bt


wallet_name = "wallet name"
wallet_hotkey = "wallet name"

platform = "twitter"
username = account


data = {
    "platform": platform,
    "account_id": account_id,
    "username": username,
    "verification_post_id": verification_post_id,
    "post_id": post_id,
    "interaction_id": interaction_id,
}

metagraph = bt.metagraph(23)

all_axons = metagraph.axons
all_validator_axons = []
for axon in all_axons:
    axon_hotkey = axon.hotkey
    if axon_hotkey not in metagraph.hotkeys:
        continue
    axon_uid = metagraph.hotkeys.index(axon_hotkey)
    if metagraph.validator_permit[axon_uid] and axon.ip != "0.0.0.0":
        all_validator_axons.append(axon)

wallet = bt.wallet(name=wallet_name, hotkey=wallet_hotkey)

# Inner method to send request to a single axon
async def send_request_to_axon(axon: bt.AxonInfo):
    url = f"http://{axon.ip}:{axon.port}/submit"  # Update with the correct URL endpoint
    request_body_bytes, request_headers = create_request(
        data=data,
        sender_keypair=wallet.hotkey,
        receiver_hotkey=axon.hotkey
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=request_headers) as response:
                if response.status == 200:
                    return {'axon': axon.hotkey, 'status': response.status, 'response': await response.json()}
                else:
                    error_message = await response.text()  # Capture response message for error details
                    return {'axon': axon.hotkey, 'status': response.status, 'error': error_message}
    except Exception as e:
        return {'axon': axon.hotkey, 'status': 'error', 'error': str(e)}

def create_request(
    data: dict[str, Any],
    sender_keypair: bt.Keypair,
    receiver_hotkey: Optional[str] = None
) -> tuple[bytes, dict[str, str]]:
    """
    Create signed request with Epistula V2 protocol.
    Returns (body_bytes, headers)
    """
    # Convert data to bytes
    body_bytes = json.dumps(data).encode("utf-8")

    # Generate timestamp and UUID
    timestamp = round(time.time() * 1000)
    timestamp_interval = ceil(timestamp / 1e4) * 1e4
    uuid_str = str(uuid4())

    # Create base headers
    headers = {
        "Epistula-Version": "2",
        "Epistula-Timestamp": str(timestamp),
        "Epistula-Uuid": uuid_str,
        "Epistula-Signed-By": sender_keypair.ss58_address,
        "Epistula-Request-Signature": "0x" + sender_keypair.sign(
            f"{sha256(body_bytes).hexdigest()}.{uuid_str}.{timestamp}.{receiver_hotkey or ''}"
        ).hex(),
    }

    # Add receiver-specific headers if signed for someone
    if receiver_hotkey:
        headers["Epistula-Signed-For"] = receiver_hotkey
        headers["Epistula-Secret-Signature-0"] = (
            "0x" + sender_keypair.sign(str(timestamp_interval - 1) + "." + receiver_hotkey).hex()
        )
        headers["Epistula-Secret-Signature-1"] = (
            "0x" + sender_keypair.sign(str(timestamp_interval) + "." + receiver_hotkey).hex()
        )
        headers["Epistula-Secret-Signature-2"] = (
            "0x" + sender_keypair.sign(str(timestamp_interval + 1) + "." + receiver_hotkey).hex()
        )

    return body_bytes, headers

# Send requests concurrently
async def main():
    tasks = [send_request_to_axon(axon) for axon in all_validator_axons]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for response in responses:
        if isinstance(response, Exception):
            print(f"Exception occurred: {response}")
        else:
            if "error" in response:
                print(f"Error while sending to axon {response['axon']}: {response['error']}")
            else:
                print(f"Successfully submitted to axon {response['axon']} with status {response['status']}")

if __name__ == "__main__":
    asyncio.run(main())     
