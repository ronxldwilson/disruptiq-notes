# Deep Fence AI Architecture

## Overview

Deep Fence is an advanced AI-powered security scanning platform designed to identify vulnerabilities in codebases through a swarm of specialized agents. The system performs comprehensive static analysis by first mapping the codebase architecture and then deploying targeted agents to detect various security threats.

## Architecture Components

### 1. Static Overview Agent
- Creates a detailed architectural diagram of the entire codebase
- Maps data flows, node connections, and systematic workflows
- Analyzes imports and dependencies
- Provides foundation for subsequent analysis

### 2. Mapper Agents
The system includes several mapper agents that specialize in different aspects:

1. **OpenAPI Specification Agent** - Generates and analyzes API specifications
2. **Raw One File Script Agent** - Analyzes standalone scripts
3. **DB Mapper Agent** - Maps database structures and relationships
4. **Network Mapper Agent** - Analyzes network configurations and communications
5. **Supply Chain Mapper Agent** - Examines dependency chains and third-party libraries
6. **Obfuscation Detector** - Identifies code obfuscation techniques
7. **Code Mapper Agent** - Maps code structures and logic flows

### 3. Attack Swarm Agents
A comprehensive collection of specialized agents targeting specific vulnerability types:

#### Web Application Security
- SQL Injection (various types: Blind, Time-based, Union-based, Boolean-based)
- Cross-Site Scripting (XSS) - Reflected, Stored, DOM-based
- Cross-Site Request Forgery (CSRF)
- Server-Side Request Forgery (SSRF)

#### Authentication & Authorization
- Broken Authentication
- Session Hijacking/Fixation
- Broken Access Control
- Privilege Escalation (Vertical/Horizontal)
- Insecure Direct Object Reference (IDOR)

#### Injection Attacks
- Remote/Local File Inclusion
- Directory Traversal
- XML External Entity (XXE)
- Server-Side Template Injection (SSTI)
- Command Injection

#### Cryptographic Issues
- Insecure Cryptographic Storage
- Weak Encryption
- Padding Oracle Attacks
- Hash Collision Attacks

#### API Security
- Insecure API Authentication
- API Rate Limiting Bypass
- Mass Assignment
- Parameter Tampering

#### Infrastructure & Network
- Man-in-the-Middle (MITM) Attacks
- DNS Spoofing/Rebinding
- ARP Spoofing
- DDoS Attacks

#### Mobile & IoT Security
- Insecure Mobile Data Storage
- Jailbreak Detection Bypass
- Bluetooth Protocol Exploits
- Firmware Vulnerabilities

#### Supply Chain & Dependencies
- Supply Chain Attacks
- Dependency Confusion
- Unpatched Software Vulnerabilities

(And many more - see full list in deep-fence/README.md)

### 4. Report Generation & Remediation
- Centralized reporting system
- Vulnerability prioritization
- Automated PR creation for fixes
- Integration with CI/CD pipelines

## Workflow Process

1. **Repository Connection**
   - Connect to GitHub repository
   - Grant necessary permissions
   - Calculate analysis cost (token usage)

2. **Architectural Mapping**
   - Deploy Static Overview Agent
   - Generate comprehensive codebase map
   - Identify critical components and data flows

3. **Specialized Analysis**
   - Deploy swarm of attack agents
   - Each agent focuses on specific vulnerability types
   - Parallel processing for efficiency

4. **Result Aggregation**
   - Collect findings from all agents
   - Identify interconnected vulnerabilities
   - Generate prioritized security report

5. **Remediation**
   - Create pull requests with fixes
   - Add commit messages
   - Integrate with GitHub Actions

## Key Features

- **Shift-Left Security**: Early vulnerability detection in development
- **Specialized Agents**: Deep expertise in specific attack vectors
- **Standalone Operation**: Agents can work independently or as part of the swarm
- **CI/CD Integration**: Automated scanning on pull requests
- **Comprehensive Coverage**: 300+ vulnerability types covered
- **Automated Remediation**: PR creation for identified issues

## Deployment Options

- **Full Swarm Mode**: Complete architectural analysis with all agents
- **Targeted Scanning**: Deploy specific agents for particular vulnerabilities
- **CI/CD Integration**: Run scans automatically on code changes
- **Standalone Agent**: Individual agents for specialized use cases

## Benefits

- Comprehensive security coverage
- Early detection of vulnerabilities
- Automated remediation suggestions
- Scalable architecture
- Integration with development workflows
- Cost-effective token usage estimation
