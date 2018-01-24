import pytest
from ethereum import tester
from tests.fixtures import *


def test_getters(contract_params, owner, wallet, token, contract):
    assert contract.call().version() == contract_version
    assert contract.call().owner_address() == owner
    assert contract.call().wallet_address() == wallet
    assert contract.call().token() == token.address
    assert contract.call().token_multiplier() == 10 ** token.call().decimals()
    assert contract.call().wei_per_token() == contract_params[0]


def test_constructor(wallet, get_accounts, get_contract, token):
    (A, B) = get_accounts(2)

    with pytest.raises(TypeError):
        get_contract([token.address, wallet, -1])
    with pytest.raises(TypeError):
        get_contract([token.address, 0x0, 2])
    with pytest.raises(TypeError):
        get_contract([token.address, fake_address, 2])
    with pytest.raises(TypeError):
        get_contract([0x0, wallet, 2])
    with pytest.raises(TypeError):
        get_contract([fake_address, wallet, 2])

    with pytest.raises(tester.TransactionFailed):
        get_contract([token.address, empty_address, 2])
    with pytest.raises(tester.TransactionFailed):
        get_contract([empty_address, wallet, 2])
    with pytest.raises(tester.TransactionFailed):
        get_contract([A, wallet, 2])

    get_contract([token.address, wallet, 2])


def test_setup(owner, wallet, get_accounts, token, contract):
    (A, B) = get_accounts(2)
    with pytest.raises(TypeError):
        contract.transact({'from': owner}).setup(-1)
    with pytest.raises(TypeError):
        contract.transact({'from': owner}).setup(MAX_UINT256 + 1)
    with pytest.raises(tester.TransactionFailed):
        contract.transact({'from': owner}).setup(0)
    with pytest.raises(tester.TransactionFailed):
        contract.transact({'from': A}).setup(10)
    with pytest.raises(tester.TransactionFailed):
        contract.transact({'from': wallet}).setup(10)

    contract.transact({'from': owner}).setup(10)


def test_setup_event(owner, contract, event_handler):
    ev_handler = event_handler(contract)

    txn_hash = contract.transact({'from': owner}).setup(10)
    ev_handler.add(txn_hash, contract_events['setup'], checkSetupEvent(10))
    ev_handler.check()
