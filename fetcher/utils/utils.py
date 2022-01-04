from ..config import EXPLORER_API_KEY
import urllib.request
import json
import urllib
import web3 as web3_module
from web3.middleware import geth_poa_middleware

blockchain_urls = {
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
}

explorer_api_link_per_blockchain = {
    "avalanche": "https://api.snowtrace.io/api?module=contract&action=getabi&address=[POOL_ABI]&apikey=[API_KEY]",
}

dex_factories = {
    "trader_joe": "0x9ad6c38be94206ca50bb0d90783181662f0cfa10",
    "pangolin": "0xefa94de7a4656d787667c749f7e1223d71e9fd88"
}

usdt_address = {
    "avalanche": "0xc7198437980c041c805a1edcba50c1ce5db95118"
}

blockchain_native_token_address = {
    "avalanche": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
}

native_token_usdt_pool = {
    "avalanche": "0xed8cbd9f0ce3c6986b22002f03c6475ceb7a6256"
}



def open_contract(web3, blockchain, address):
    link = explorer_api_link_per_blockchain[blockchain].replace("[POOL_ABI]", address).replace("[API_KEY]", EXPLORER_API_KEY[blockchain])
    addressABI = json.loads(urllib.request.urlopen(link).read())["result"]
    return web3.eth.contract(address=web3.toChecksumAddress(address), abi=addressABI)

def get_block_average_time(web3, span=100):
    times = []
    current_number = web3.eth.block_number
    try:
        first_block = web3.eth.get_block(current_number - span)
    except web3_module.exceptions.ExtraDataLengthError:
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        first_block = web3.eth.get_block(current_number - span)
    prev_timestamp = first_block.timestamp
    average_time = 0

    for i in range(current_number - span + 1, current_number):
        block = web3.eth.get_block(i)
        time = block.timestamp - prev_timestamp
        prev_timestamp = block.timestamp
        average_time += time/span
    return average_time


def calculate_token_price(web3, blockchain, pool_address, source_token_address):
    liquidityContract = open_contract(web3, blockchain, pool_address)
    reserves = liquidityContract.functions.getReserves().call()
    reserveToken0 = reserves[0]
    reserveToken1 = reserves[1]
    token0Address = liquidityContract.functions.token0().call()
    token1Address = liquidityContract.functions.token1().call() 
    try:
        token0 = open_contract(web3, blockchain, token0Address)
        token0Decimals = token0.functions.decimals().call()
    except:
        token0Decimals = 18
    try:
        token1 = open_contract(web3, blockchain, token1Address)
        token1Decimals = token1.functions.decimals().call()
    except:
        token1Decimals = 18
    if token0Address == source_token_address:
        price = (reserveToken1 * 10**-token1Decimals) / (reserveToken0 * 10**-token0Decimals)
    else :
        price = (reserveToken0 * 10**-token0Decimals) / (reserveToken1 * 10**-token1Decimals)
    return price


def get_token_price_from_dexs(web3, blockchain, token_address):
    if token_address == blockchain_native_token_address[blockchain]:
        return calculate_token_price(web3, blockchain, native_token_usdt_pool[blockchain], token_address)
    elif token_address == usdt_address[blockchain]:
        return 1
    contracts = {}
    prices = []
    for dex_factory_key, dex_factory in dex_factories.items(): 
        dex_factory_contract = open_contract(web3, blockchain, dex_factory)
        contracts[dex_factory_key] = dex_factory_contract
        pair_address = dex_factory_contract.functions.getPair(web3.toChecksumAddress(token_address), web3.toChecksumAddress(usdt_address[blockchain])).call()
        if int(pair_address, 16) != 0:
            price = calculate_token_price(web3, blockchain, pair_address, token_address)
            prices.append(price)
    if prices != []:
        return min(prices)
    # Try with native blockchain token
    for dex_factory_key, dex_factory in dex_factories.items():
        dex_factory_contract = contracts[dex_factory_key]
        pair_address = dex_factory_contract.functions.getPair(web3.toChecksumAddress(token_address), web3.toChecksumAddress(blockchain_native_token_address[blockchain])).call()
        if int(pair_address, 16) != 0:
            price_in_native_token = calculate_token_price(web3, blockchain, pair_address, token_address)
            price_of_native_token_in_usdt = calculate_token_price(web3, blockchain, native_token_usdt_pool[blockchain], blockchain_native_token_address[blockchain])
            prices.append(price_in_native_token * price_of_native_token_in_usdt)
    if prices != []:
        return min(prices)
    return -1
