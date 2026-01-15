const hre = require("hardhat");

async function main() {
  console.log("🚀 Starting deployment...\n");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("📍 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");

  // Deploy MockERC20 token
  console.log("📦 Deploying MockERC20 token...");
  const MockERC20 = await hre.ethers.getContractFactory("MockERC20");
  const token = await MockERC20.deploy(
    "DeFi Test Token",
    "DTEST",
    hre.ethers.parseEther("1000000")
  );
  await token.waitForDeployment();
  const tokenAddress = await token.getAddress();
  console.log("✅ MockERC20 deployed to:", tokenAddress);

  // Deploy TokenVault
  console.log("\n📦 Deploying TokenVault...");
  const TokenVault = await hre.ethers.getContractFactory("TokenVault");
  const vault = await TokenVault.deploy();
  await vault.waitForDeployment();
  const vaultAddress = await vault.getAddress();
  console.log("✅ TokenVault deployed to:", vaultAddress);

  // Add token to supported list
  console.log("\n⚙️  Configuring vault...");
  const tx = await vault.addSupportedToken(tokenAddress);
  await tx.wait();
  console.log("✅ Added token to supported list");

  // Mint some tokens to deployer
  console.log("\n💎 Minting tokens...");
  const mintTx = await token.mint(deployer.address, hre.ethers.parseEther("10000"));
  await mintTx.wait();
  console.log("✅ Minted 10,000 tokens to deployer");

  // Print summary
  console.log("\n" + "=".repeat(60));
  console.log("📋 DEPLOYMENT SUMMARY");
  console.log("=".repeat(60));
  console.log("MockERC20 Token:", tokenAddress);
  console.log("TokenVault:     ", vaultAddress);
  console.log("Deployer:       ", deployer.address);
  console.log("=".repeat(60));

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      MockERC20: tokenAddress,
      TokenVault: vaultAddress
    }
  };

  fs.writeFileSync(
    "deployment.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n💾 Deployment info saved to deployment.json");

  // Verification instructions
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\n📝 To verify contracts on Etherscan, run:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${tokenAddress} "DeFi Test Token" "DTEST" "${hre.ethers.parseEther("1000000")}"`);
    console.log(`npx hardhat verify --network ${hre.network.name} ${vaultAddress}`);
  }

  console.log("\n✨ Deployment complete!\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
