import pytest
from ethereum import tester
from tests.fixtures import *


buy_values = [
    # wei value, wei_per_token
    (1, 1),
    (1, 10 ** 18),
    (10 ** 18, 421761 * 10 ** 10),
    (10 ** 10, 421761 * 10 ** 10),
]


@pytest.fixture(params=buy_values)
def buy_value_fixtures(request):
    return request.param


def test_buy_value0(web3, get_accounts, token, funded_contract):
    (A, B) = get_accounts(2)
    assert token.call().balanceOf(funded_contract.address) > 0
    with pytest.raises(tester.TransactionFailed):
        funded_contract.transact({'from': A, 'value': 0}).buy(A)
    with pytest.raises(tester.TransactionFailed):
        txn_hash = web3.eth.sendTransaction({
            'from': A,
            'to': funded_contract.address,
            'value': 0
        })


def test_buy_delegate(get_accounts, token, funded_contract):
    (A, B) = get_accounts(2)
    assert token.call().balanceOf(funded_contract.address) >= 10
    funded_contract.transact({'from': A, 'value': 10}).buy(A)
    funded_contract.transact({'from': A, 'value': 10})
    funded_contract.transact({'from': B, 'value': 10}).buy(B)
    funded_contract.transact({'from': B, 'value': 10})
    funded_contract.transact({'from': B, 'value': 10}).buy(A)
    funded_contract.transact({'from': A, 'value': 10}).buy(B)


def test_buy_no_funds(web3, get_accounts, wallet, token, contract):
    (A, B) = get_accounts(2)
    assert token.call().balanceOf(contract.address) == 0
    with pytest.raises(tester.TransactionFailed):
        contract.transact({'from': A, 'value': 1}).buy(A)
    with pytest.raises(tester.TransactionFailed):
        txn_hash = web3.eth.sendTransaction({
            'from': B,
            'to': contract.address,
            'value': 1
        })

    token.transact({'from': wallet}).transfer(contract.address, 5 * 10 ** 18)
    assert token.call().balanceOf(contract.address) == 5 * 10 ** 18
    value = 6 * contract.call().wei_per_token()

    with pytest.raises(tester.TransactionFailed):
        contract.transact({'from': A, 'value': value}).buy(A)
    with pytest.raises(tester.TransactionFailed):
        txn_hash = web3.eth.sendTransaction({
            'from': B,
            'to': contract.address,
            'value': value
        })


def test_buy_state(web3, get_accounts, owner, wallet, token, funded_contract, buy_value_fixtures, txn_cost, print_gas):
    (A, B) = get_accounts(2)
    (value, wei_per_token) = buy_value_fixtures
    multiplier = token.call().multiplier()

    funded_contract.transact({'from': owner}).setup(wei_per_token)
    assert wei_per_token == funded_contract.call().wei_per_token()

    pre_A_token_balance = token.call().balanceOf(A)
    pre_A_wei_balance = web3.eth.getBalance(A)
    pre_B_token_balance = token.call().balanceOf(B)
    pre_B_wei_balance = web3.eth.getBalance(B)
    pre_contract_token_balance = token.call().balanceOf(funded_contract.address)
    pre_contract_wei_balance = web3.eth.getBalance(funded_contract.address)
    pre_wallet_token_balance = token.call().balanceOf(wallet)
    pre_wallet_wei_balance = web3.eth.getBalance(wallet)
    pre_owner_token_balance = token.call().balanceOf(owner)
    pre_owner_wei_balance = web3.eth.getBalance(owner)

    tokens_expected = value * multiplier // wei_per_token

    assert web3.eth.getBalance(A) >= value
    assert token.call().balanceOf(funded_contract.address) >= tokens_expected

    txn_hash = funded_contract.transact({'from': A, 'value': value}).buy(A)
    txn_wei = txn_cost(txn_hash)

    assert token.call().balanceOf(A) == pre_A_token_balance + tokens_expected
    assert web3.eth.getBalance(A) == pre_A_wei_balance - value - txn_wei
    assert token.call().balanceOf(funded_contract.address) == pre_contract_token_balance - tokens_expected
    assert web3.eth.getBalance(funded_contract.address) == pre_contract_wei_balance
    assert token.call().balanceOf(wallet) == pre_wallet_token_balance
    assert web3.eth.getBalance(wallet) == pre_wallet_wei_balance + value
    assert token.call().balanceOf(owner) == pre_owner_token_balance
    assert web3.eth.getBalance(owner) == pre_owner_wei_balance

    print_gas(txn_hash, 'buy {} TKN for {} ETH'.format(
        tokens_expected / 10 ** 18,
        value / 10 ** 18
    ))

    assert web3.eth.getBalance(B) >= value
    assert token.call().balanceOf(funded_contract.address) >= tokens_expected

    txn_hash = web3.eth.sendTransaction({
        'from': B,
        'to': funded_contract.address,
        'value': value
    })
    txn_wei = txn_cost(txn_hash)

    assert token.call().balanceOf(B) == pre_B_token_balance + tokens_expected
    assert web3.eth.getBalance(B) == pre_B_wei_balance - value - txn_wei
    assert token.call().balanceOf(funded_contract.address) == pre_contract_token_balance - 2 * tokens_expected
    assert web3.eth.getBalance(funded_contract.address) == pre_contract_wei_balance
    assert token.call().balanceOf(wallet) == pre_wallet_token_balance
    assert web3.eth.getBalance(wallet) == pre_wallet_wei_balance + 2 * value
    assert token.call().balanceOf(owner) == pre_owner_token_balance
    assert web3.eth.getBalance(owner) == pre_owner_wei_balance

    print_gas(txn_hash, 'fallback buy {} TKN for {} ETH'.format(
        tokens_expected / 10 ** 18,
        value / 10 ** 18
    ))


def test_buy_event(web3, owner, wallet, get_accounts, token, funded_contract, event_handler):
    (A, B) = get_accounts(2)
    ev_handler = event_handler(funded_contract)
    multiplier = token.call().multiplier()
    wei_per_token = funded_contract.call().wei_per_token()
    value = 10000000
    tokens_expected = value * multiplier // wei_per_token

    txn_hash = funded_contract.transact({'from': A, 'value': value}).buy(A)
    ev_handler.add(txn_hash, contract_events['buy'], checkBuyEvent(A, value, tokens_expected))

    txn_hash = web3.eth.sendTransaction({
        'from': B,
        'to': funded_contract.address,
        'value': value
    })
    ev_handler.add(txn_hash, contract_events['buy'], checkBuyEvent(B, value, tokens_expected))
    ev_handler.check()
