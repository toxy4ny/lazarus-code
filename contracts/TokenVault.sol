// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TokenVault
 * @dev A vault contract for depositing and withdrawing ERC20 tokens
 * @notice This contract has a deliberate vulnerability for educational purposes
 * 
 * CHALLENGE: Find and fix the reentrancy vulnerability
 */
contract TokenVault is Ownable, ReentrancyGuard {
    // Mapping from user address to token address to balance
    mapping(address => mapping(address => uint256)) public balances;
    
    // Total deposits per token
    mapping(address => uint256) public totalDeposits;
    
    // Supported tokens
    mapping(address => bool) public supportedTokens;
    
    // Events
    event Deposit(address indexed user, address indexed token, uint256 amount);
    event Withdrawal(address indexed user, address indexed token, uint256 amount);
    event TokenAdded(address indexed token);
    event TokenRemoved(address indexed token);
    
    constructor() Ownable(msg.sender) {}
    
    /**
     * @dev Add a token to the list of supported tokens
     * @param token Address of the ERC20 token
     */
    function addSupportedToken(address token) external onlyOwner {
        require(token != address(0), "Invalid token address");
        require(!supportedTokens[token], "Token already supported");
        
        supportedTokens[token] = true;
        emit TokenAdded(token);
    }
    
    /**
     * @dev Remove a token from the list of supported tokens
     * @param token Address of the ERC20 token
     */
    function removeSupportedToken(address token) external onlyOwner {
        require(supportedTokens[token], "Token not supported");
        
        supportedTokens[token] = false;
        emit TokenRemoved(token);
    }
    
    /**
     * @dev Deposit tokens into the vault
     * @param token Address of the ERC20 token
     * @param amount Amount of tokens to deposit
     */
    function deposit(address token, uint256 amount) external nonReentrant {
        require(supportedTokens[token], "Token not supported");
        require(amount > 0, "Amount must be greater than 0");
        
        IERC20 tokenContract = IERC20(token);
        require(
            tokenContract.transferFrom(msg.sender, address(this), amount),
            "Transfer failed"
        );
        
        balances[msg.sender][token] += amount;
        totalDeposits[token] += amount;
        
        emit Deposit(msg.sender, token, amount);
    }
    
    /**
     * @dev Withdraw tokens from the vault
     * @param token Address of the ERC20 token
     * @param amount Amount of tokens to withdraw
     * 
     * ⚠️ VULNERABILITY: This function is vulnerable to reentrancy attack
     * The balance is updated AFTER the external call, allowing an attacker
     * to recursively call withdraw before the balance is updated
     */
    function withdraw(address token, uint256 amount) external {
        require(supportedTokens[token], "Token not supported");
        require(amount > 0, "Amount must be greater than 0");
        require(balances[msg.sender][token] >= amount, "Insufficient balance");
        
        IERC20 tokenContract = IERC20(token);
        
        // VULNERABILITY: External call before state update
        // An attacker can create a malicious token that calls back into withdraw
        // during the transfer, draining the vault
        require(
            tokenContract.transfer(msg.sender, amount),
            "Transfer failed"
        );
        
        // State update happens AFTER external call - this is the vulnerability!
        balances[msg.sender][token] -= amount;
        totalDeposits[token] -= amount;
        
        emit Withdrawal(msg.sender, token, amount);
    }
    
    /**
     * @dev Withdraw all tokens of a specific type
     * @param token Address of the ERC20 token
     */
    function withdrawAll(address token) external {
        uint256 balance = balances[msg.sender][token];
        require(balance > 0, "No balance to withdraw");
        
        withdraw(token, balance);
    }
    
    /**
     * @dev Get the balance of a user for a specific token
     * @param user Address of the user
     * @param token Address of the ERC20 token
     * @return The balance of the user
     */
    function getBalance(address user, address token) external view returns (uint256) {
        return balances[user][token];
    }
    
    /**
     * @dev Get the total deposits for a specific token
     * @param token Address of the ERC20 token
     * @return The total deposits
     */
    function getTotalDeposits(address token) external view returns (uint256) {
        return totalDeposits[token];
    }
    
    /**
     * @dev Emergency withdrawal function for owner
     * @param token Address of the ERC20 token
     * @param amount Amount to withdraw
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20 tokenContract = IERC20(token);
        require(
            tokenContract.transfer(owner(), amount),
            "Transfer failed"
        );
    }
}