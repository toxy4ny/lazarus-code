# Contributing Guide

Thank you for participating in our technical assessment! This guide will help you submit your solution.

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Node.js v18 or higher installed
- ✅ Git configured on your machine
- ✅ VS Code or your preferred IDE
- ✅ Basic understanding of Solidity and smart contract security

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/[YOUR-ORG]/defi-vault-audit-challenge.git
cd defi-vault-audit-challenge
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Tests

```bash
npm test
```

You should see some tests passing and potentially some failing due to the vulnerability.

### 4. Compile Contracts

```bash
npm run compile
```

## 🔍 Your Task

### Step 1: Analyze the Code

Carefully review `contracts/TokenVault.sol` and identify the security vulnerability.

**Hint:** Pay special attention to:
- State changes
- External calls
- Function execution order
- Reentrancy patterns

### Step 2: Document Your Findings

Create a detailed analysis in `SOLUTION.md` including:
- Vulnerability description
- Attack scenario
- Severity assessment
- Proof of concept (optional)

### Step 3: Implement the Fix

Modify `contracts/TokenVault.sol` to fix the vulnerability while maintaining functionality.

**Requirements:**
- ✅ Fix must address the root cause
- ✅ All existing tests must pass
- ✅ Code must remain readable and maintainable
- ✅ Gas efficiency should be considered

### Step 4: Test Your Solution

```bash
# Run all tests
npm test

# Run with gas reporting
REPORT_GAS=true npm test

# Run coverage
npm run coverage
```

### Step 5: Add New Tests (Bonus)

Add test cases that specifically validate your fix prevents the attack.

## 📤 Submission Process

### 1. Create a New Branch

```bash
git checkout -b solution/your-name
```

### 2. Commit Your Changes

```bash
git add .
git commit -m "Fix: Resolve reentrancy vulnerability in TokenVault"
```

### 3. Push Your Branch

```bash
git push origin solution/your-name
```

### 4. Create a Pull Request

- Go to the repository on GitHub
- Click "New Pull Request"
- Select your branch
- Fill in the PR template with:
  - Summary of changes
  - Link to your SOLUTION.md
  - Test results
  - Any additional notes

## 📝 Submission Checklist

Before submitting, ensure:

- [ ] Vulnerability is properly identified and documented
- [ ] Fix is implemented in `TokenVault.sol`
- [ ] `SOLUTION.md` is complete and detailed
- [ ] All tests pass (`npm test`)
- [ ] Code is properly formatted (`npm run format`)
- [ ] No linting errors (`npm run lint`)
- [ ] Pull request is created with clear description

## 🎯 Evaluation Criteria

Your submission will be evaluated on:

1. **Security Knowledge (40%)**
   - Correct identification of vulnerability
   - Understanding of attack vectors
   - Severity assessment accuracy

2. **Solution Quality (30%)**
   - Effectiveness of the fix
   - Code quality and readability
   - Gas efficiency considerations

3. **Documentation (20%)**
   - Clarity of explanation
   - Completeness of analysis
   - Professional presentation

4. **Testing (10%)**
   - Test coverage
   - Edge case consideration
   - Validation of fix

## 💡 Tips

- **Take your time:** Quality is more important than speed
- **Think like an attacker:** Consider all possible exploit scenarios
- **Research:** Use external resources (SWC Registry, OpenZeppelin, etc.)
- **Be thorough:** Document your thought process
- **Ask questions:** If something is unclear, reach out to us

## 📚 Recommended Resources

- [Consensys Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [SWC Registry](https://swcregistry.io/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Solidity Security Considerations](https://docs.soliditylang.org/en/latest/security-considerations.html)

## ❓ Questions?

If you have any questions during the assessment:

- **Email:** recruitment@defi-innovations.io
- **Telegram:** @DeFiInnovationsHR
- **Response time:** Within 24 hours

## ⏰ Timeline

- **Time allowed:** 48 hours from repository access
- **Expected completion time:** 2-4 hours
- **Deadline:** [Will be communicated separately]

---

**Good luck! We're excited to review your solution.** 🚀

*DeFi Innovations Team*
