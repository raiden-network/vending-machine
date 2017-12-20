pragma solidity ^0.4.19;

import './Token.sol';

contract SimpleExchange {

    address public owner_address;
    Token public token;

    uint256 public wei_limit_per_address = 10 ** 18 * 2;
    uint256 public wei_per_token_fraction = 1;

    mapping (address => uint256) public wei_per_address;


    /*
     * Modifiers
     */

    modifier isOwner() {
        require(msg.sender == owner_address);
        _;
    }

    function SimpleExchange(address _token_address) public {
        require(_token_address != 0x0);
        require(addressHasCode(_token_address));

        token = Token(_token_address);

        // Check if the contract is indeed a token contract
        require(token.totalSupply() > 0);

        owner_address = msg.sender;
    }

    function () external payable {
        require(msg.value > 0);
        require(wei_per_address[msg.sender] + msg.value < wei_limit_per_address);
        require(wei_per_address[msg.sender] + msg.value >= msg.value);

        wei_per_address[msg.sender] += msg.value;
        uint256 number_of_tokens = msg.value / wei_per_token_fraction;
        require(token.transfer(msg.sender, number_of_tokens));
    }

    function tokenFallback(address _sender_address, uint256 _deposit, bytes _data) external {
        // Make sure we trust the token
        require(msg.sender == address(token));
    }

    function setWeiPerTokenFraction(uint256 _wei_per_token_fraction) external isOwner {
        require(_wei_per_token_fraction > 0);
        wei_per_token_fraction = _wei_per_token_fraction;
    }

    function empty() external isOwner {
        uint256 contract_balance = token.balanceOf(address(this));
        require(token.transfer(owner_address, contract_balance));
    }

    /// @dev Check if a contract exists.
    /// @param _contract The address of the contract to check for.
    /// @return True if a contract exists, false otherwise
    function addressHasCode(address _contract) internal constant returns (bool) {
        uint size;
        assembly {
            size := extcodesize(_contract)
        }

        return size > 0;
    }
}
