import time
from web3 import Web3
import json
import os
import smtplib
import urllib
import web3 as web3_module
from web3.middleware import geth_poa_middleware
from config import EXPLORER_API_KEY



 

def farm_list_sorted_by_apr_from_masterchef(masterchef_address, blockchain, token_dapp_address_function, token_per_block_function):
    
    web3 = Web3(Web3.HTTPProvider(blockchain_urls[blockchain]))
    farms = []
    masterchef_contract = open_contract(web3, blockchain, masterchef_address)
    # Get dapp token address and pre-compute some data (generation block average time, annual token emission...
    token_address = getattr(masterchef_contract.functions, token_dapp_address_function)().call()
    total_alloc_point = masterchef_contract.functions.totalAllocPoint().call()
    tokenContract = open_contract(web3, blockchain, token_address)
    decimals = tokenContract.functions.decimals().call()
    average_time_per_block_seconds = get_block_average_time(web3, span=200)
    block_per_seconds = 1.0 / average_time_per_block_seconds
    block_per_year = block_per_seconds * 3600 * 24 * 365
    token_per_block = getattr(masterchef_contract.functions, token_per_block_function)().call()
    annual_token_emission = block_per_year * (token_per_block/(10**decimals))
    # Fetch each pool of the masterchef
    for i in range(masterchef_contract.functions.poolLength().call()):
        pool_info = masterchef_contract.functions.poolInfo(i).call()
        totalStaked = pool_info[-1]
        pool_address = pool_info[0]
        alloc_point = pool_info[1]
        # Compute infos about pool (emission share and reward amount per year)
        pool_emission_share = alloc_point / total_alloc_point
        pool_reward_amount_per_year = annual_token_emission * pool_emission_share
        # Compute price of the dapp token
        price_token = get_token_price_from_dexs(web3, blockchain, dex_factories.values(), token_address, usdt_address[blockchain])
        
        # Get price and decimals of a single-asset or LP token
        pool_contract = open_contract(web3, blockchain, pool_address)
        if "token0" not in dir(pool_contract.functions):
            token0Symbol = pool_contract.functions.symbol().call()
            token1Symbol = pool_contract.functions.symbol().call()
            LPToken_price = get_token_price_from_dexs(web3, blockchain, dex_factories.values(), pool_address, usdt_address[blockchain]) if pool_address.lower() != usdt_address[blockchain].lower() else 1
            LPToken_decimals = pool_contract.functions.decimals().call()
        else:
            token0Address = pool_contract.functions.token0().call()
            token1Address = pool_contract.functions.token1().call()
            token0 = open_contract(web3, blockchain, token0Address)
            token1 = open_contract(web3, blockchain, token1Address)
            token_0_price = get_token_price_from_dexs(web3, blockchain, dex_factories.values(), token0Address, usdt_address[blockchain]) if token0Address.lower() != usdt_address[blockchain].lower() else 1
            token_1_price = get_token_price_from_dexs(web3, blockchain, dex_factories.values(), token1Address, usdt_address[blockchain]) if token1Address.lower() != usdt_address[blockchain].lower() else 1
            token0Decimals = token0.functions.decimals().call()
            token1Decimals = token1.functions.decimals().call()
            token0Symbol = token0.functions.symbol().call()
            token1Symbol = token1.functions.symbol().call()
            reserves = pool_contract.functions.getReserves().call()
            reserveToken0 = reserves[0]*10**-(token0Decimals)
            reserveToken1 = reserves[1]*10**-(token1Decimals)
            totalSupply = pool_contract.functions.totalSupply().call()*10**-pool_contract.functions.decimals().call()
            componentLPToken0 = reserveToken0 / totalSupply
            componentLPToken1 = reserveToken1 / totalSupply
            LPToken_price = componentLPToken0 * token_0_price + componentLPToken1 * token_1_price
            LPToken_decimals = pool_contract.functions.decimals().call()
            
            
        # Finally, compute farm APR   
        pool_reward_value_per_year = price_token * pool_reward_amount_per_year
        total_value_locked = (totalStaked*10**-LPToken_decimals) * LPToken_price
        apr = pool_reward_value_per_year*100/total_value_locked
        token_symbol_tuple = token0Symbol+"/"+token1Symbol if token0Symbol != token1Symbol else token0Symbol
        dict_farm = {
            "name": token_symbol_tuple,
            "apr": apr,
            "tvl": total_value_locked
        }
        farms.append(dict_farm)
    return sorted(farms, key=lambda x: x["apr"], reverse=True)
    
if __name__ == "__main__":
    print("test")
    print(farm_list_sorted_by_apr_from_masterchef("0x64aB872a2937dE057F21c8e0596C0175FF2084d8", "avalanche", "banksy", "banksyPerBlock"))
    
    
    
    
    
    
    
    
    
    
    
    

