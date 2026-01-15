# 🚀 DeFi Vault - Smart Contract Security Audit Challenge

<div align="center">

![DeFi Innovations](https://img.shields.io/badge/DeFi-Innovations-blue?style=for-the-badge)
![Solidity](https://img.shields.io/badge/Solidity-0.8.20-363636?style=for-the-badge&logo=solidity)
![Hardhat](https://img.shields.io/badge/Hardhat-2.19.0-yellow?style=for-the-badge)

**Building the Future of Decentralized Finance**

</div>

---

## 👋 Welcome, Candidate!

Thank you for your interest in the **Senior Blockchain Developer** position at DeFi Innovations. This technical assessment will evaluate your ability to identify and fix critical security vulnerabilities in smart contracts.

## 🎯 The Challenge

Our TokenVault contract has been flagged by our internal security team for a potential **reentrancy vulnerability**. Your mission:

1. **Analyze** the smart contract code in `contracts/TokenVault.sol`
2. **Identify** the security vulnerability
3. **Implement** a secure fix
4. **Write** a brief explanation of the issue and your solution
5. **Submit** your solution within 48 hours

## 🛠️ Setup Instructions

### Prerequisites
- Node.js v18+ and npm
- VS Code (recommended)
- Basic understanding of Solidity and DeFi concepts

### Quick Start

```bash
# Clone the repository
git clone https://github.com/[YOUR-ORG]/defi-vault-audit-challenge.git
cd defi-vault-audit-challenge

# Install dependencies
npm install

# Open in VS Code
code .

# Run tests
npm test

# Compile contracts
npm run compile
```

## 📂 Project Structure

```
defi-vault-audit-challenge/
├── contracts/
│   ├── TokenVault.sol          # Main contract with vulnerability
│   └── interfaces/
│       └── IERC20.sol
├── test/
│   └── TokenVault.test.js      # Test suite
├── scripts/
│   └── deploy.js               # Deployment script
├── hardhat.config.js
└── package.json
```

## 🔍 What We're Looking For

- **Security awareness**: Can you spot the vulnerability?
- **Problem-solving skills**: How do you approach the fix?
- **Code quality**: Is your solution clean and well-documented?
- **Testing**: Do you validate your fix properly?

## 📝 Submission Guidelines

1. Create a new branch: `git checkout -b solution/your-name`
2. Fix the vulnerability in `TokenVault.sol`
3. Add your explanation to `SOLUTION.md`
4. Ensure all tests pass: `npm test`
5. Push your branch and create a Pull Request

## 💰 Position Details

- **Role**: Senior Blockchain Developer
- **Location**: Remote (Global)
- **Compensation**: $180,000 - $220,000 + equity
- **Tech Stack**: Solidity, Hardhat, TypeScript, React, Node.js

## 📞 Questions?

Contact our recruitment team:
- **Email**: recruitment@defi-innovations.io
- **Telegram**: @DeFiInnovationsHR

---

<div align="center">

**Good luck! We're excited to see your solution.** 🎉

*DeFi Innovations © 2026 | [Website](https://defi-innovations.io) | [Careers](https://defi-innovations.io/careers)*

</div>
