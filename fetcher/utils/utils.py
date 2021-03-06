from web3.main import Web3
from ..config import EXPLORER_API_KEY
import urllib.request
import json
import urllib
import web3 as web3_module
from web3.middleware import geth_poa_middleware
import time

blockchain_urls = {
    "avalanche": "https://speedy-nodes-nyc.moralis.io/5dd5cce6646e002a1a9c9272/avalanche/mainnet",
    "binance_smart_chain": "https://speedy-nodes-nyc.moralis.io/5dd5cce6646e002a1a9c9272/bsc/mainnet"
}

explorer_api_link_per_blockchain = {
    "avalanche": "https://api.snowtrace.io/api?module=contract&action=getabi&address=[POOL_ABI]&apikey=[API_KEY]",
    "binance_smart_chain": "https://api.bscscan.com/api?module=contract&action=getabi&address=[POOL_ABI]&apikey=[API_KEY]"
}

dex_factories = {
    "avalanche": {
        "trader_joe": "0x9ad6c38be94206ca50bb0d90783181662f0cfa10",
        "pangolin": "0xefa94de7a4656d787667c749f7e1223d71e9fd88",
        "lydia": "0xe0c1bb6df4851feeedc3e14bd509feaf428f7655",
    },
    "binance_smart_chain": {
        "pancakeswap": "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
    }
}

usdt_address = {
    "avalanche": "0xc7198437980c041c805a1edcba50c1ce5db95118",
    "binance_smart_chain": "0x55d398326f99059fF775485246999027B3197955"
}

blockchain_native_token_address = {
    "avalanche": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    "binance_smart_chain": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
}

native_token_usdt_pool = {
    "avalanche": "0xed8cbd9f0ce3c6986b22002f03c6475ceb7a6256",
    "binance_smart_chain": "0x16b9a82891338f9ba80e2d6970fdda79d1eb0dae"
}

platform_name_mapping = {
    "JLP": "traderjoe",
    "PGL": "pangolin",
    "Lydia-LP": "lydiafinance"
}

decimals_mapping = {
    "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e": 6,
    "0x4e840aadd28da189b9906674b4afcb77c128d9ea": 18
}

symbol_mapping = {
    "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e": "USDC",
    "0x4e840aadd28da189b9906674b4afcb77c128d9ea": "SISTA",
    "0xb27c8941a7df8958a1778c0259f76d1f8b711c35": "KLO",
    "0x9e037de681cafa6e661e6108ed9c2bd1aa567ecd": "WALBT",
    "0x938fe3788222a74924e062120e7bfac829c719fb": "APEIN",
    "0x027dbca046ca156de9622cd1e2d907d375e53aa7": "AMPL",
    "0x1c20e891bab6b1727d14da358fae2984ed9b59eb": "TUSD",
    "0x01c2086facfd7aa38f69a6bd8c91bef3bb5adfca": "YAY",
    "0xa384bc7cdc0a93e686da9e7b8c0807cd040f4e0b": "WOW",
    "0xea6887e4a9cda1b77e70129e5fba830cdb5cddef": "IMX.a",
    "0x544c42fbb96b39b21df61cf322b5edc285ee7429": "INSUR",
    "0x340fe1d898eccaad394e2ba0fc1f93d27c7b717a": "ORBS",
    "0x346a59146b9b4a77100d369a3d18e8007a9f46a6": "AVAI",
    "0x9e3ca00f2d4a9e5d4f0add0900de5f15050812cf": "NFTD",
    "0xf891214fdcf9cdaa5fdc42369ee4f27f226adad6": "IME",
    "0xe0ce60af0850bf54072635e66e79df17082a1109": "ICE",
    "0x78c42324016cd91d1827924711563fb66e33a83a": "RELAY"
}

price_mapping = {}

already_opened_contract = {}

token_bridger = {
    ("avalanche", "binance_smart_chain"):{
        "0x4e840aadd28da189b9906674b4afcb77c128d9ea": "0xca6d25c10dad43ae8be0bc2af4d3cd1114583c08"
    }
}

particular_case_lp_tokens_price = {
    "tuplets": {
        "0x0665eF3556520B21368754Fb644eD3ebF1993AD4".lower(): (
            "0x7f90122BF0700F9E7e1F688fe926940E8839F353", "balances", "underlying_coins", "0x1337bedc9d22ecbe766df105c9623922a27963ec"
        ),
        "0x3a7387f8ba3ebffa4a0eccb1733e940ce2275d3f".lower(): (
            "0x2a716c4933A20Cd8B9f9D9C39Ae7196A85c24228", "getTokenBalance", "getToken", "0x3a7387f8ba3ebffa4a0eccb1733e940ce2275d3f"
        ),
        "0x4da067E13974A4d32D342d86fBBbE4fb0f95f382".lower(): (
            "0x8c3c1C6F971C01481150CA7942bD2bbB9Bc27bC7", "getTokenBalance", "getToken", "0x4da067E13974A4d32D342d86fBBbE4fb0f95f382"
        ),
        "0xc161E4B11FaF62584EFCD2100cCB461A2DdE64D1".lower(): (
            "0x90c7b96AD2142166D001B27b5fbc128494CDfBc8", "getTokenBalance", "getToken", "0xc161E4B11FaF62584EFCD2100cCB461A2DdE64D1"
        ),
        "0xaD556e7dc377d9089C6564f9E8d275f5EE4da22d".lower(): (
            "0x6EfbC734D91b229BE29137cf9fE531C1D3bf4Da6", "getTokenBalance", "getToken", "0xaD556e7dc377d9089C6564f9E8d275f5EE4da22d"
        ),
        "0xA57E0D32Aa27D3b1D5AFf6a8A786C6A4DADb818F".lower(): (
            "0x26694e4047eA77cC96341f0aC491773aC5469d72", "getTokenBalance", "getToken", "0xA57E0D32Aa27D3b1D5AFf6a8A786C6A4DADb818F"
        )
    }
}

qitoken_mapping = {
    "0x5c0401e81bc07ca70fad469b451682c0d747ef1c": "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7",
    "0xe194c4c5ac32a3c9ffdb358d9bfd523a0b6d1568": "0x50b7545627a5162f82a992c33b87adc75187b218",
    "0x334ad834cd4481bb02d09615e7c11a00579a7909": "0x49d5c2bdffac6ce2bfdb6640f4f80f226bc10bab",
    "0xc9e5999b8e75c3feb117f6f73e664b9f3c8ca65c": "0xc7198437980c041c805a1edcba50c1ce5db95118",
    "0x4e9f683a27a6bdad3fc2764003759277e93696e6": "0x5947bb275c521040051d82396192181b413227a3",
    "0x835866d37afb8cb8f8334dccdaf66cf01832ff5d": "0xd586e7f844cea2f87f50152665bcbc2c279d8d70",
    "0xbeb5d47a3f720ec0a390d04b4d41ed7d9688bc7f": "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664",
    "0x35bd6aeda81a7e5fc7a7832490e71f757b0cd9ce": "0x8729438eb15e2c8b576fcc6aecda6a148776c0f5"
}


def open_contract(web3, blockchain, address, providedABI = None):
    global already_opened_contract
    if web3.toChecksumAddress(address) in already_opened_contract:
        return already_opened_contract[web3.toChecksumAddress(address)]
    while True:
        if providedABI is None:
            link = explorer_api_link_per_blockchain[blockchain].replace("[POOL_ABI]", address).replace("[API_KEY]", EXPLORER_API_KEY[blockchain])
            addressABI = json.loads(urllib.request.urlopen(link).read())["result"]
        else:
            addressABI = providedABI
        if addressABI == "Contract source code not verified":
            return None
        elif addressABI == "Max rate limit reached, rate limit of 5/1sec applied":
            time.sleep(1.0/5.0)
            continue
        break

    contract = web3.eth.contract(address=web3.toChecksumAddress(address), abi=addressABI)
    already_opened_contract[web3.toChecksumAddress(address)] = contract
    return contract



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


def calculate_token_price(web3, blockchain, pool_address, source_token_address, opened_contract=None):
    global decimals_mapping
    liquidity_contract = opened_contract
    if liquidity_contract is None:
        liquidity_contract = open_contract(web3, blockchain, pool_address)
    reserves = liquidity_contract.functions.getReserves().call()
    reserve_token0 = reserves[0]
    reserve_token1 = reserves[1]
    if min(reserves) == 0:
        return -1 
    token0_address = liquidity_contract.functions.token0().call()
    token1_address = liquidity_contract.functions.token1().call() 
    try:
        token0 = open_contract(web3, blockchain, token0_address)
        token0_decimals = token0.functions.decimals().call()
    except:
        token0_decimals = decimals_mapping.get(token0_address.lower(), 18)
    try:
        token1 = open_contract(web3, blockchain, token1_address)
        token1_decimals = token1.functions.decimals().call()
    except:
        token1_decimals = decimals_mapping.get(token1_address.lower(), 18)
    if token0_address.lower() == source_token_address.lower():
        price = (reserve_token1 * 10**-token1_decimals) / (reserve_token0 * 10**-token0_decimals)
    elif token1_address.lower() == source_token_address.lower() :
        price = (reserve_token0 * 10**-token0_decimals) / (reserve_token1 * 10**-token1_decimals)
    else:
        price = -1
    return price


def calculate_lp_token_price(web3, blockchain, pool_address, opened_contract=None):
    global decimals_mapping
    pool_contract = opened_contract
    if pool_contract is None:
        pool_contract = open_contract(web3, blockchain, pool_address)
    if "token0" not in dir(pool_contract.functions):
        return get_token_price_from_dexs(web3, blockchain, pool_address)
    token0_address = pool_contract.functions.token0().call()
    token1_address = pool_contract.functions.token1().call()
    token_0_price = get_token_price_from_dexs(web3, blockchain, token0_address) if token0_address.lower() != usdt_address[blockchain].lower() else 1
    token_1_price = get_token_price_from_dexs(web3, blockchain, token1_address) if token1_address.lower() != usdt_address[blockchain].lower() else 1
    token0 = None
    token1 = None
    try:
        token0 = open_contract(web3, blockchain, token0_address)
    except:
        token0_decimals = decimals_mapping.get(token0_address.lower(), 18)
    try:
        token1 = open_contract(web3, blockchain, token1_address)
    except:
        token1_decimals = decimals_mapping.get(token1_address.lower(), 18)

    if token0 is not None and "decimals" in dir(token0.functions):
        token0_decimals = token0.functions.decimals().call()
    else:
        token0_decimals = decimals_mapping.get(token0_address.lower(), 18)

    if token1 is not None and "decimals" in dir(token1.functions):
        token1_decimals = token1.functions.decimals().call()
    else:
        token1_decimals = decimals_mapping.get(token1_address.lower(), 18)

    reserves = pool_contract.functions.getReserves().call()
    reserve_token0 = reserves[0]*10**-(token0_decimals)
    reserve_token1 = reserves[1]*10**-(token1_decimals)
    total_supply = pool_contract.functions.totalSupply().call()*(10**-pool_contract.functions.decimals().call())
    component_lp_token0 = reserve_token0 / total_supply
    component_lp_token1 = reserve_token1 / total_supply
    return component_lp_token0 * token_0_price + component_lp_token1 * token_1_price


def get_token_price_from_dexs(web3, blockchain, token_address, exclude_others_blockchains = []):
    global price_mapping
    if token_address.lower() in price_mapping:
        return price_mapping[token_address.lower()]
    if token_address.lower() == usdt_address[blockchain]:
        return 1
    contracts = {}
    prices = []
    weight_pools = []
    for dex_factory_key, dex_factory in dex_factories[blockchain].items(): 
        dex_factory_contract = open_contract(web3, blockchain, dex_factory)
        contracts[dex_factory_key] = dex_factory_contract
        pair_address = dex_factory_contract.functions.getPair(web3.toChecksumAddress(token_address), web3.toChecksumAddress(usdt_address[blockchain])).call()
        if int(pair_address, 16) != 0:
            price = calculate_token_price(web3, blockchain, pair_address, token_address)
            if price != -1:
                prices.append(price)
                weight_pools.append(sum(open_contract(web3, blockchain, pair_address).functions.getReserves().call()[:-1]))
    if token_address.lower() != blockchain_native_token_address[blockchain]:
        # Try with native blockchain token
        for dex_factory_key, dex_factory in dex_factories[blockchain].items():
            dex_factory_contract = contracts[dex_factory_key]
            pair_address = dex_factory_contract.functions.getPair(web3.toChecksumAddress(token_address), web3.toChecksumAddress(blockchain_native_token_address[blockchain])).call()
            if int(pair_address, 16) != 0:
                price_in_native_token = calculate_token_price(web3, blockchain, pair_address, token_address)
                price_of_native_token_in_usdt = calculate_token_price(web3, blockchain, native_token_usdt_pool[blockchain], blockchain_native_token_address[blockchain])
                if price_of_native_token_in_usdt != -1:
                    prices.append(price_in_native_token * price_of_native_token_in_usdt)
                    weight_pools.append(sum(open_contract(web3, blockchain, pair_address).functions.getReserves().call()[:-1]))
    total_weight_pools = sum(weight_pools)
    weights = [w/total_weight_pools for w in weight_pools]
    prices = [prices[i] * weights[i] for i in range(len(prices))]
    price_mapping[token_address] = sum(prices) if len(prices) > 0 else -1
    if price_mapping[token_address] == -1:
        for other_blockchain in blockchain_urls.keys():
            if other_blockchain != blockchain and other_blockchain not in exclude_others_blockchains:
                token_address_bridged = None
                if (blockchain, other_blockchain) in token_bridger and token_address.lower() in token_bridger[(blockchain, other_blockchain)]:
                    token_address_bridged = token_bridger[(blockchain, other_blockchain)][token_address.lower()]
                elif (other_blockchain, blockchain) in token_bridger and token_address.lower() in token_bridger[(other_blockchain, blockchain)]:
                    token_address_bridged = token_bridger[(other_blockchain, blockchain)][token_address.lower()]
                if token_address_bridged is not None:
                    price_mapping[token_address] = get_token_price_from_dexs(
                        Web3(Web3.HTTPProvider(blockchain_urls[other_blockchain])),
                        other_blockchain,
                        token_address_bridged,
                        exclude_others_blockchains=exclude_others_blockchains + [blockchain]
                    )
                if price_mapping[token_address] != -1:
                    return price_mapping[token_address]
    return price_mapping[token_address]


def calculate_special_token_price(web3, blockchain, pool_address):
    global particular_case_lp_tokens_price
    if pool_address.lower() in particular_case_lp_tokens_price["tuplets"]:
        tuplet_address, balance_field, underlyingcoin_field, lp_supply_contract = particular_case_lp_tokens_price["tuplets"][pool_address.lower()]
        lp_contract = open_contract(web3, blockchain, lp_supply_contract)
        decimals = lp_contract.functions.decimals().call()
        total_supply = open_contract(web3, blockchain, lp_supply_contract).functions.totalSupply().call() * 10**-decimals
        tuplet_contract = open_contract(web3, blockchain, tuplet_address)
        i = 0
        price = 0
        underlyingcoin_price = 0
        while True:
            try:
                underlyingcoin_address = getattr(tuplet_contract.functions, underlyingcoin_field)(i).call()
                underlyingcoin_contract = open_contract(web3, blockchain, underlyingcoin_address)
                if "decimals" in dir(underlyingcoin_contract.functions):
                    underlyingcoin_decimals = underlyingcoin_contract.functions.decimals().call()
                elif "decimals" in dir(tuplet_contract.functions):
                    underlyingcoin_decimals = tuplet_contract.functions.decimals().call()
                else:
                    underlyingcoin_decimals = decimals_mapping.get(underlyingcoin_address.lower(), decimals_mapping.get(tuplet_address.lower(), 18))
                underlyingcoin_price_try = calculate_lp_token_price(web3, blockchain, underlyingcoin_address)
                if underlyingcoin_price_try == -1:
                    underlyingcoin_price = calculate_special_token_price(web3, blockchain, underlyingcoin_address)
                else:
                    underlyingcoin_price = underlyingcoin_price_try
                price += ((getattr(tuplet_contract.functions, balance_field)(i).call() * 10**-underlyingcoin_decimals)/total_supply) * underlyingcoin_price
            except Exception as e:
                print(e)
                break
            i += 1
        return price
    return -1
