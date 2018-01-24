import pytest
from ethereum import tester
from tests.fixtures import *


def test_withdraw_call(owner, wallet, get_accounts, token, funded_contract):
    (A, B) = get_accounts(2)
    with pytest.raises(tester.TransactionFailed):
        funded_contract.transact({'from': owner}).withdrawTokens()
    with pytest.raises(tester.TransactionFailed):
        funded_contract.transact({'from': A}).withdrawTokens()

    funded_contract.transact({'from': wallet}).withdrawTokens()


def test_withdraw_state(owner, wallet, token, funded_contract):
    owner_pre_balance = token.call().balanceOf(owner)
    wallet_pre_balance = token.call().balanceOf(wallet)
    contract_balance = token.call().balanceOf(funded_contract.address)
    assert contract_balance > 0

    funded_contract.transact({'from': wallet}).withdrawTokens()
    assert token.call().balanceOf(funded_contract.address) == 0
    assert token.call().balanceOf(wallet) == wallet_pre_balance + contract_balance
    assert token.call().balanceOf(owner) == owner_pre_balance


def test_withdraw_tokens_event(owner, wallet, token, contract, event_handler):
    ev_handler = event_handler(contract)

    balance = token.call().balanceOf(contract.address)
    txn_hash = contract.transact({'from': wallet}).withdrawTokens()

    ev_handler.add(txn_hash, contract_events['withdraw'], checkWithdrawTokensEvent(balance))
    ev_handler.check()
