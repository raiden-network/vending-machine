import pytest
from ethereum import tester
from eth_utils import encode_hex
from tests.fixtures import *


def test_token_fallback_deposit0(owner, wallet, token, contract):
    with pytest.raises(tester.TransactionFailed):
        token.transact({'from': wallet}).transfer(contract.address, 0, encode_hex(bytearray()))
    token.transact({'from': wallet}).transfer(contract.address, 1000, encode_hex(bytearray()))

def test_token_fallback_untrusted_token(owner, wallet, token, contract, get_token_contract):
    other_token = get_token_contract([10 ** 26, 'CustomToken2', 'TKN', 18])
    other_token.transact({'from': owner}).transfer(wallet, 1000)
    assert other_token.call().balanceOf(wallet) == 1000

    with pytest.raises(tester.TransactionFailed):
        other_token.transact({'from': wallet}).transfer(contract.address, 1000, encode_hex(bytearray()))

    assert token.call().balanceOf(wallet) >= 1000
    token.transact({'from': wallet}).transfer(contract.address, 1000, encode_hex(bytearray()))


def test_token_fallback_not_wallet(owner, wallet, get_accounts, token, contract):
    (A, B) = get_accounts(2)
    assert token.call().balanceOf(owner) >= 1000
    with pytest.raises(tester.TransactionFailed):
        token.transact({'from': owner}).transfer(contract.address, 1000, encode_hex(bytearray()))

    token.transact({'from': owner}).transfer(A, 1000)
    assert token.call().balanceOf(A) == 1000
    with pytest.raises(tester.TransactionFailed):
        token.transact({'from': A}).transfer(contract.address, 1000, encode_hex(bytearray()))


def test_token_fallback_state(owner, wallet, token, contract):
    token.transact({'from': wallet}).transfer(contract.address, 1000, encode_hex(bytearray()))
    assert token.call().balanceOf(contract.address) == 1000


def test_token_fallback_event(owner, wallet, token, contract, event_handler):
    ev_handler = event_handler(contract)

    txn_hash = token.transact({'from': wallet}).transfer(contract.address, 1000, encode_hex(bytearray()))

    ev_handler.add(txn_hash, contract_events['fund'], checkFundEvent(1000))
    ev_handler.check()


def test_token_fallback_print_gas_cost(wallet, token, contract, print_gas):
    txn_hash = token.transact({'from': wallet}).transfer(contract.address, 10 ** 20, encode_hex(bytearray()))
    print_gas(txn_hash, 'fund contract with 100 TKN')
