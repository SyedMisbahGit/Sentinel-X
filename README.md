# ARBITER // System Integrity Evaluator (v2.0)

> **"Advanced External Attack Surface Management and Automated Red Teaming Framework."**

ARBITER is a highly modular, stateful, and memory-efficient reconnaissance and vulnerability discovery engine. Designed to operate flawlessly on low-resource environments (like minimal Kali VMs) while targeting massive enterprise scopes, ARBITER replaces disjointed bash scripts with a unified, SQLite-backed Python intelligence pipeline. 

It does not just dump raw data; it cross-references findings, filters out false positives via auto-calibration, and actively hunts for high-impact bug bounty vectors.

---

## 🧠 Core Architecture

* **The SQLite Memory Core:** ARBITER abandons legacy JSON/RAM storage. It streams tens of thousands of subdomains, IPs, and endpoints directly to a local SQLite database utilizing Write-Ahead Logging (WAL) and memory-piping. It can process 100,000+ assets with virtually zero RAM footprint.
* **Stateful Execution:** Built-in mission tracking. If a scan drops or a WAF blocks your IP, ARBITER resumes exactly where it left off.
* **The Ghost Protocol:** At the conclusion of an evaluation, ARBITER can interactively purge all local `.db` files and output logs, leaving zero trace of the mission on the host machine.
* **Subprocess RAM Piping:** Integrates with powerful Go binaries (`httpx`, `naabu`, `subfinder`, `ffuf`) but routes all data through standard input/output streams rather than temporary disk files, eliminating disk thrashing.

---

## ⚔️ The Execution Pipeline (Subsystems)

ARBITER operates in sequential, intelligent phases. Later phases dynamically adapt based on intelligence gathered in earlier phases.

### Phase 1: Surface Mapping
* **Phase 1.1 - Horizontal Recon:** Resolves the origin IP, queries global BGP routing tables to identify the target's Autonomous System Number (ASN), and extracts all associated IPv4 CIDR blocks. (Includes a Cloud Shield to prevent scanning shared infrastructure).
* **Phase 1.2 - Infrastructure Forensics:** Deep DNS structural analysis. Hunts for AXFR Zone Transfers (feeding results back into the scanner), NS Hijacking (dangling nameservers), legacy DNSSEC NSEC walking, and mines TXT records for exposed verification tokens.
* **Phase 1.5 - The CDN Shield & Port Scanning:** Evaluates all domains for Cloudflare/AWS routing. Bypasses deep scanning on CDN-fronted hosts to save time, piping direct-origin IPs into `Naabu` for aggressive port sweeps.
* **Phase 1.8 - Permutations:** Generates and resolves hidden development and staging environment naming conventions to uncover Shadow IT.

### Phase 2: Active Profiling
* **Phase 2.0 - The Tech Profiler:** Streams live targets through `HTTPX` (with WAF-evasion agents) to extract server identities, status codes, and underlying technologies (e.g., WordPress, React, IIS).
* **Phase 2.2 - The Asynchronous Spider:** A high-speed `aiohttp` crawler that maps internal URL structures and extracts hidden endpoints without falling into infinite crawler traps.
* **Phase 2.5 - Cloud Recon:** Hunts for unprotected S3, Azure, and GCP storage buckets tied to the target's brand footprint.
* **Phase 2.7 - SpoofCheck:** Analyzes DMARC/SPF configurations for CEO Fraud vulnerabilities, generating weaponized `swaks` Proof-of-Concept commands for internal spoofing tests.
* **Phase 2.8 - GitHub Intelligence:** Interfaces with the GitHub REST API using advanced dorking to hunt for leaked AWS keys, database passwords, and API tokens across public repositories.

### Phase 3 & 4: Neural Extraction & Offensive Strikes
* **Phase 3.0 - Cortex (Neural JS Extraction):** Downloads JavaScript bundles and utilizes Shannon Entropy calculations to differentiate between actual cryptographic secrets and random webpack hashes, drastically reducing false positives. Actively probes extracted API endpoints for 200 OK responses.
* **Phase 4.0 - CORS Cartographer:** Dynamically tests Cross-Origin Resource Sharing configurations to identify API hijacking vulnerabilities.
* **Phase 4.5 - Reflection Cartography:** Injects canary payloads into discovered parameters (from the Spider) to identify unescaped HTML reflections (Pre-XSS vectors).
* **Phase 4.8 - The OAST Protocol:** Hunts for Blind Server-Side Request Forgery (SSRF) and Out-of-Band interactions by poisoning HTTP headers with unique RequestRepo tracking payloads.

### Phase 5: Chaos
* **Phase 5.0 - Auto-Calibrated Content Discovery:** Directory fuzzing using `FFUF`. Armed with Auto-Calibration to detect when a server is lying (Soft-404s/Catch-Alls), filtering out the noise to deliver strictly validated assets.

---

## 🛡️ Disclaimer
ARBITER is an automated security evaluation tool. It is designed strictly for authorized penetration testing, bug bounty hunting on sanctioned programs, and academic security research. The operators assume no liability for the misuse of this framework.
