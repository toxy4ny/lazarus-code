const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");

describe("TokenVault", function () {
  
  async function deployVaultFixture() {
    const [owner, user1, user2, attacker] = await ethers.getSigners();
    
    const MockERC20 = await ethers.getContractFactory("MockERC20");
    const token = await MockERC20.deploy(
      "Test Token",
      "TEST",
      ethers.parseEther("1000000")
    );

    const TokenVault = await ethers.getContractFactory("TokenVault");
    const vault = await TokenVault.deploy();

    await vault.addSupportedToken(await token.getAddress());

    await token.mint(user1.address, ethers.parseEther("10000"));
    await token.mint(user2.address, ethers.parseEther("10000"));
    await token.mint(attacker.address, ethers.parseEther("10000"));

    return { vault, token, owner, user1, user2, attacker };
  }

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      const { vault, owner } = await loadFixture(deployVaultFixture);
      expect(await vault.owner()).to.equal(owner.address);
    });

    it("Should add token to supported list", async function () {
      const { vault, token } = await loadFixture(deployVaultFixture);
      expect(await vault.supportedTokens(await token.getAddress())).to.be.true;
    });
  });

  describe("Token Management", function () {
    it("Should allow owner to add supported token", async function () {
      const { vault, owner } = await loadFixture(deployVaultFixture);
      
      const MockERC20 = await ethers.getContractFactory("MockERC20");
      const newToken = await MockERC20.deploy("New Token", "NEW", ethers.parseEther("1000"));
      
      await expect(vault.addSupportedToken(await newToken.getAddress()))
        .to.emit(vault, "TokenAdded")
        .withArgs(await newToken.getAddress());
      
      expect(await vault.supportedTokens(await newToken.getAddress())).to.be.true;
    });

    it("Should not allow non-owner to add supported token", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);
      
      const MockERC20 = await ethers.getContractFactory("MockERC20");
      const newToken = await MockERC20.deploy("New Token", "NEW", ethers.parseEther("1000"));
      
      await expect(
        vault.connect(user1).addSupportedToken(await newToken.getAddress())
      ).to.be.revertedWithCustomError(vault, "OwnableUnauthorizedAccount");
    });

    it("Should allow owner to remove supported token", async function () {
      const { vault, token } = await loadFixture(deployVaultFixture);
      
      await expect(vault.removeSupportedToken(await token.getAddress()))
        .to.emit(vault, "TokenRemoved")
        .withArgs(await token.getAddress());
      
      expect(await vault.supportedTokens(await token.getAddress())).to.be.false;
    });
  });

  describe("Deposits", function () {
    it("Should allow users to deposit tokens", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      const depositAmount = ethers.parseEther("100");
      await token.connect(user1).approve(await vault.getAddress(), depositAmount);
      
      await expect(vault.connect(user1).deposit(await token.getAddress(), depositAmount))
        .to.emit(vault, "Deposit")
        .withArgs(user1.address, await token.getAddress(), depositAmount);
      
      expect(await vault.getBalance(user1.address, await token.getAddress())).to.equal(depositAmount);
    });

    it("Should update total deposits correctly", async function () {
      const { vault, token, user1, user2 } = await loadFixture(deployVaultFixture);
      
      const amount1 = ethers.parseEther("100");
      const amount2 = ethers.parseEther("200");
      
      await token.connect(user1).approve(await vault.getAddress(), amount1);
      await vault.connect(user1).deposit(await token.getAddress(), amount1);
      
      await token.connect(user2).approve(await vault.getAddress(), amount2);
      await vault.connect(user2).deposit(await token.getAddress(), amount2);
      
      expect(await vault.getTotalDeposits(await token.getAddress())).to.equal(amount1 + amount2);
    });

    it("Should revert if token is not supported", async function () {
      const { vault, user1 } = await loadFixture(deployVaultFixture);
      
      const MockERC20 = await ethers.getContractFactory("MockERC20");
      const unsupportedToken = await MockERC20.deploy("Unsupported", "UNS", ethers.parseEther("1000"));
      
      await expect(
        vault.connect(user1).deposit(await unsupportedToken.getAddress(), ethers.parseEther("100"))
      ).to.be.revertedWith("Token not supported");
    });

    it("Should revert if amount is zero", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      await expect(
        vault.connect(user1).deposit(await token.getAddress(), 0)
      ).to.be.revertedWith("Amount must be greater than 0");
    });
  });

  describe("Withdrawals", function () {
    it("Should allow users to withdraw tokens", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      const depositAmount = ethers.parseEther("100");
      await token.connect(user1).approve(await vault.getAddress(), depositAmount);
      await vault.connect(user1).deposit(await token.getAddress(), depositAmount);
      
      const withdrawAmount = ethers.parseEther("50");
      await expect(vault.connect(user1).withdraw(await token.getAddress(), withdrawAmount))
        .to.emit(vault, "Withdrawal")
        .withArgs(user1.address, await token.getAddress(), withdrawAmount);
      
      expect(await vault.getBalance(user1.address, await token.getAddress())).to.equal(depositAmount - withdrawAmount);
    });

    it("Should allow users to withdraw all tokens", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      const depositAmount = ethers.parseEther("100");
      await token.connect(user1).approve(await vault.getAddress(), depositAmount);
      await vault.connect(user1).deposit(await token.getAddress(), depositAmount);
      
      await vault.connect(user1).withdrawAll(await token.getAddress());
      
      expect(await vault.getBalance(user1.address, await token.getAddress())).to.equal(0);
    });

    it("Should revert if insufficient balance", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      await expect(
        vault.connect(user1).withdraw(await token.getAddress(), ethers.parseEther("100"))
      ).to.be.revertedWith("Insufficient balance");
    });
  });

  describe("Reentrancy Attack", function () {
    it("Should demonstrate the reentrancy vulnerability", async function () {
      const { vault, attacker } = await loadFixture(deployVaultFixture);
      
      // Deploy malicious token
      const MaliciousToken = await ethers.getContractFactory("MaliciousToken");
      const malToken = await MaliciousToken.connect(attacker).deploy();
      
      // Add malicious token to vault
      await vault.addSupportedToken(await malToken.getAddress());
      
      // Setup attack
      await malToken.connect(attacker).setVault(await vault.getAddress());
      await malToken.connect(attacker).setMaxAttacks(3);
      
      // Deposit tokens
      const depositAmount = ethers.parseEther("100");
      await malToken.connect(attacker).approve(await vault.getAddress(), depositAmount);
      await vault.connect(attacker).deposit(await malToken.getAddress(), depositAmount);
      
      // Enable attack and withdraw
      await malToken.connect(attacker).enableAttack();
      
      // This should demonstrate the vulnerability
      // In a real scenario, this would drain more than the deposited amount
      await vault.connect(attacker).withdraw(await malToken.getAddress(), ethers.parseEther("10"));
      
      // Check if attack succeeded (balance should be manipulated)
      const finalBalance = await vault.getBalance(attacker.address, await malToken.getAddress());
      console.log("Balance after attack:", ethers.formatEther(finalBalance));
    });
  });

  describe("Emergency Functions", function () {
    it("Should allow owner to emergency withdraw", async function () {
      const { vault, token, user1, owner } = await loadFixture(deployVaultFixture);
      
      const depositAmount = ethers.parseEther("100");
      await token.connect(user1).approve(await vault.getAddress(), depositAmount);
      await vault.connect(user1).deposit(await token.getAddress(), depositAmount);
      
      const ownerBalanceBefore = await token.balanceOf(owner.address);
      await vault.emergencyWithdraw(await token.getAddress(), depositAmount);
      const ownerBalanceAfter = await token.balanceOf(owner.address);
      
      expect(ownerBalanceAfter - ownerBalanceBefore).to.equal(depositAmount);
    });

    it("Should not allow non-owner to emergency withdraw", async function () {
      const { vault, token, user1 } = await loadFixture(deployVaultFixture);
      
      await expect(
        vault.connect(user1).emergencyWithdraw(await token.getAddress(), ethers.parseEther("100"))
      ).to.be.revertedWithCustomError(vault, "OwnableUnauthorizedAccount");
    });
  });
});