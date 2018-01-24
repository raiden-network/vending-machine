import pytest
from eth_utils import encode_hex
from tests.fixtures import *


contract_version = '0.1.0'
wallet_token_fractions =  10 ** 22
contract_token_fractions = wallet_token_fractions
contract_events = {
    'setup': 'Setup',
    'fund': 'Fund',
    'buy': 'Buy',
    'withdraw': 'WithdrawTokens'
}
contract_args = [
    # _wei_per_token
    [421761 * 10 ** 10]
]


@pytest.fixture(params=contract_args)
def contract_params(request):
    return request.param


@pytest.fixture()
def get_contract(chain, create_contract):
    def get(arguments, transaction=None):
        VendingMachine = chain.provider.get_contract_factory('VendingMachine')
        contract = create_contract(
            VendingMachine,
            arguments,
            transaction
        )

        if print_the_logs:
            print_logs(uraiden_contract, 'Setup', 'VendingMachine')
            print_logs(uraiden_contract, 'Fund', 'VendingMachine')
            print_logs(uraiden_contract, 'Buy', 'VendingMachine')
            print_logs(uraiden_contract, 'WithdrawTokens', 'VendingMachine')

        return contract
    return get


@pytest.fixture()
def token(chain, get_token_contract):
    return get_token_contract([10 ** 26, 'CustomToken', 'TKN', 18])


@pytest.fixture()
def wallet(web3, wallet_address, owner, token):
    token.transact({'from': owner}).transfer(wallet_address, wallet_token_fractions, encode_hex(bytearray()))
    return wallet_address


@pytest.fixture()
def contract(chain, owner, wallet, token, get_contract, contract_params):
    params = [token.address, wallet] + contract_params
    return get_contract(params, {'from': owner})


@pytest.fixture()
def funded_contract(chain, wallet, token, contract):
    token.transact({'from': wallet}).transfer(contract.address, contract_token_fractions)
    return contract


def checkFundEvent(token_fractions):
    def get(event):
        assert event['args']['_token_fractions'] == token_fractions
    return get


def checkSetupEvent(wei_per_token):
    def get(event):
        assert event['args']['_wei_per_token'] == wei_per_token
    return get


def checkBuyEvent(buyer, value, wei_per_token):
    def get(event):
        assert event['args']['_buyer'] == buyer
        assert event['args']['_value'] == value
        assert event['args']['_token_fractions'] == token_fractions
    return get


def checkWithdrawTokensEvent(token_fractions):
    def get(event):
        assert event['args']['_token_fractions'] == token_fractions
    return get
