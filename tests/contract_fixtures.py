import pytest
from eth_utils import encode_hex
from tests.fixtures import (
    owner_index,
    owner,
    create_contract
)

contract_version = '0.1.0'
wallet_token_fractions = 100 * 10 ** 18
contract_token_fractions = wallet_token_fractions
contract_events = {
    'setup': 'Setup',
    'fund': 'Fund',
    'buy': 'Buy',
    'withdraw': 'WithdrawTokens'
}
contract_args = [
    # (_wei_max_per_address, _wei_per_token)
    (2 * 10 ** 18, 421761 * 10 ** 10)
]



@pytest.fixture(params=contract_args)
def contract_params(request):
    return request.param


@pytest.fixture()
def get_contract(chain, create_contract):
    def get(arguments, transaction=None):
        Contract = chain.provider.get_contract_factory('SimpleExchange')
        contract = create_contract(
            SimpleExchange,
            arguments,
            transaction
        )

        if print_the_logs:
            print_logs(uraiden_contract, 'Setup', 'SimpleExchange')
            print_logs(uraiden_contract, 'Fund', 'SimpleExchange')
            print_logs(uraiden_contract, 'Buy', 'SimpleExchange')
            print_logs(uraiden_contract, 'WithdrawTokens', 'SimpleExchange')

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
def contract(chain, owner, get_contract, contract_params):
    return get_contract(contract_params, {'from': owner})


@pytest.fixture()
def funded_contract(chain, wallet, token, contract):
    token.transact({'from': wallet}).transfer(contract.address, contract_token_fractions)
    return contract
