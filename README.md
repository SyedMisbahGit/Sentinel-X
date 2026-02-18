# ARBITER // v2.0
**SYSTEM INTEGRITY EVALUATOR**

> *The Verdict is Final.*

**ARBITER** is an offensive security framework designed for high-speed Red Teaming, automated reconnaissance, and business logic validation. It does not just scan; it issues a **Protocol Determination** on the target's security posture.

## ⚡ Core Capabilities

* **Protocol Determination:** Issues a graded Security Diagnostic (CRITICAL / COMPROMISED / OPTIMAL).
* **SpoofCheck:** Validates CEO Fraud vectors (DMARC/SPF) and generates `swaks` PoC commands.
* **The Seizure:** Automated Subdomain Takeover detection via `Nuclei`.
* **Deep Cover:** JavaScript Endpoint Extraction & Secret Mining (`Cortex`).
* **Shadow IT:** Subdomain Permutation Engine to find hidden dev/stage environments.
* **Trace Deletion:** Interactive prompt to purge all mission data upon completion.

---

## 💀 Kali Execution Protocols

**1. System Diagnostic (Standard Mode)**
```bash
python arbiter.py scan tesla.com --mode standard

2. Ghost Protocol (Stealth Mode)
Bash

python arbiter.py scan tesla.com --mode stealth

3. Resume Interrupted Session
Bash

python arbiter.py scan tesla.com --resume

4. System Integrity Check
Bash

python verify_config.py

📂 Output Intelligence

Arbiter generates a Heads-Up Display (HUD) report:

    Path: output/TARGET/arbiter_log.html

    Data: Live Nodes, Hidden API Endpoints, Email Spoofing Status, and Critical Anomalies.

⚠️ Disclaimer

Authorized Testing Only. The user assumes all liability for the use of this weapon.
