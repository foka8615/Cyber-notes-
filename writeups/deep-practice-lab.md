# Lab Report #003 — OSI Model Drilling & Unknown Host Enumeration
**Date:** 2026-06-08
**Analyst:** foka8615
**Platform:** Sharp S7-SH | Android 11 | Termux (no-root)
**Target:** Home Network (192.168.1.0/24) + Unknown Host (192.168.1.139)
**Status:** Completed
**Methodology:** OODA Loop (Observe → Orient → Decide → Act)

---

## 1. Objectives
- Drill OSI layer mapping through live command execution
- Correct misconceptions about layer/protocol assignments
- Enumerate unknown host 192.168.1.139 using available tools
- Test port connectivity using netcat
- Attempt OS fingerprinting and full port scan
- Document all findings, limitations, and methodology

### Why This Matters
Every layer of the OSI model is an attack surface.
Connecting theoretical knowledge to live tool behavior
builds the mental model required for real threat analysis.
Unknown host enumeration simulates the discovery phase
of a real engagement where an analyst finds an unexpected
device on a network.

---

## 2. Environment

### Analyst Device
| Property | Value |
|----------|-------|
| Device | Sharp S7-SH |
| OS | Android 11 |
| Root | No (locked bootloader) |
| Tool Platform | Termux |
| Timezone | WAT (UTC+1) |

### Tools Used
| Tool | Version | Purpose | OSI Layer |
|------|---------|---------|-----------|
| nmap | 7.99 | Port/service/OS scanning | L3/L4 |
| netcat (nc) | 7.99 | Port connectivity testing | L4 |
| dig | 9.20.23 | DNS queries | L7 |
| nslookup | 9.20.23 | Reverse DNS lookup | L7 |
| netstat | 2.10.0 | Active connection listing | L4 |
| telnet | — | Protocol testing | L7 |
| ifconfig | 2.10.0 | Interface/MAC info | L2 |
| ping | — | ICMP host discovery | L3 |
| tracepath | — | Route tracing | L3 |

---

## 3. Methodology — OODA Loop Applied

### Observe
Run commands, collect raw terminal output, take screenshots.
No interpretation during collection — evidence first.

### Orient
Map each command to its OSI layer and protocol.
Identify what each result means in a security context.
Compare expected vs actual behavior.

### Decide
Determine follow-up tests based on findings.
Prioritize anomalies (unknown host, port reappearance).
Identify what root access would unlock.

### Act
Execute next test. Document result. Loop repeats.
Every unexpected result becomes a new observation.

---

## 4. Phase 1 — OSI Layer Drilling

### Exercise Format
Predict layer, protocol, and attack vector BEFORE running.
Then run and compare theory vs reality.
This is how professionals build accurate mental models.

### Commands Tested
ping -c 3 192.168.1.1
dig google.com
nmap -sn 192.168.1.0/24
ifconfig
netstat -tulnp

### Round 1 — Layer Identification
| Command | Predicted Layer | Correct Layer | Verdict | Explanation |
|---------|----------------|---------------|---------|-------------|
| ping | L3 | L3 | CORRECT | ICMP operates at Network layer |
| dig | L7 | L7 | CORRECT | DNS is Application layer |
| nmap -sn | L4 | L3 | WRONG | Ping sweep uses ICMP not ports |
| ifconfig | L1 | L2 | WRONG | Shows MAC addresses = Data Link |
| netstat | L2 | L4 | WRONG | Shows TCP/UDP ports = Transport |

### Round 1 — Protocol Identification
| Command | Predicted | Correct | Verdict | Explanation |
|---------|-----------|---------|---------|-------------|
| ping | IP | ICMP | WRONG | IP carries ICMP — ICMP IS the protocol |
| dig | TCP | UDP/53 | WRONG | DNS uses UDP by default, TCP only >512B |
| nmap -sn | TCP | ICMP | WRONG | Ping sweep = ICMP echo requests automated |
| ifconfig | ARP | Ethernet 802.3 | WRONG | ARP resolves IP to MAC, ifconfig shows 802.3 |
| netstat | IP | TCP/UDP | PARTIAL | Shows both protocols |

### Round 1 — Attack Vector Identification
| Layer | Predicted Attack | Correct Attack | Verdict |
|-------|-----------------|---------------|---------|
| L3 | IP Spoofing | IP Spoofing | CORRECT |
| L7 | SQL Injection | SQL Injection / DNS Hijacking | CORRECT |
| L4 | Unknown | SYN Flood / Port Scanning | MISSING |
| L1 | Physical threat | Wiretapping / Hardware implant | CORRECT |
| L2 | Unknown | ARP Poisoning / MAC Flooding | MISSING |

### Score: 6/15 — Round 1

### Key Misconceptions Corrected
| Concept | Wrong Model | Correct Model |
|---------|------------|---------------|
| ping protocol | IP | ICMP — IP is carrier, ICMP is payload |
| dig protocol | TCP | UDP/53 by default |
| nmap -sn layer | L4 ports | L3 ICMP — no ports involved |
| ifconfig layer | L1 physical | L2 MAC addresses |
| netstat layer | L2 data link | L4 TCP/UDP ports |
| L4 attack | None recalled | SYN flood — floods TCP handshakes |
| L2 attack | None recalled | ARP poisoning — fake MAC to IP mappings |

### Corrected OSI Command Reference
| Command | Layer | Protocol | Primary Attack |
|---------|-------|----------|---------------|
| ping | L3 | ICMP | IP spoofing, ICMP flood |
| dig | L7 | UDP/53 | DNS hijacking, cache poisoning |
| nmap -sn | L3 | ICMP | ICMP flood, ping sweep detection |
| ifconfig | L2 | Ethernet 802.3 | ARP poisoning, MAC flooding |
| netstat | L4 | TCP/UDP | SYN flood, port scanning |
| tracepath | L3 | ICMP/UDP | Route manipulation, TTL abuse |
| nmap -sV | L4/L7 | TCP + app probes | Service exploitation |
| nc (netcat) | L4 | TCP/UDP | Port probing, banner grabbing |
| nslookup | L7 | UDP/53 | DNS spoofing |

---

## 5. Phase 2 — netstat Failure Analysis

### Command
netstat -tulnp

### Result
netstat: no support for AF INET (tcp) on this system.

### Why It Failed
Android kernel does not expose /proc/net/tcp and
/proc/net/udp to unprivileged processes. Termux without
root cannot access kernel-level socket tables.
Root access required for full socket enumeration on Android.

### Workaround
ss -tulnp
ss (socket statistics) accesses different kernel interfaces
and may work without root on some Android versions.

---

## 6. Phase 3 — Telnet Analysis

### Command
telnet
telnet> quit

### Finding
Telnet binary available in Termux. Running bare telnet
opens interactive prompt with no connection established.
Requires target host and port to be useful.

### Telnet vs SSH Security Comparison
| Property | Telnet | SSH |
|----------|--------|-----|
| Encryption | None | Full |
| Layer | L7 | L7 |
| Port | 23/tcp | 22/tcp |
| Protocol | TCP | TCP |
| Credentials | Plaintext | Encrypted |
| Use today | Deprecated | Standard |

### Attack Scenario
Any attacker performing ARP poisoning (L2) on the same
network can capture complete Telnet sessions including
usernames and passwords in cleartext using tcpdump.
This is why Telnet was replaced by SSH in all production
environments.

---

## 7. Phase 4 — Unknown Host Enumeration (192.168.1.139)

### Discovery Context
Host 192.168.1.139 appeared on network during session.
Not present in Lab 001 or Lab 002 scans.
Identity unknown. Full enumeration attempted.

### Why This Matters
Unknown hosts on a network are a critical security concern.
They may represent unauthorized devices, IoT devices with
default credentials, guest devices, or active attackers.
Standard procedure: enumerate fully before concluding.

### Attempt 1 — OS Fingerprint Scan
Command: nmap -sV -sC -O 192.168.1.139
Result: TCP/IP fingerprinting (for OS scan) requires root privileges. QUITTING!
Analysis: -O flag requires raw packet crafting = root only.
No root = no OS fingerprinting. Hard Android limitation.
Layer affected: L3 (IP packet construction)

### Attempt 2 — Full Port Scan
Command: nmap -p- 192.168.1.139
Result: Still running after 11 minutes at 7.15% completion.
ETC showed 2+ hours remaining. Cancelled with Ctrl+C.

Why So Slow:
-p- scans all 65,535 ports via TCP connect scan.
No root = no SYN scan. Each filtered port waits for timeout.

| Scan Type | Root Required | Speed | Method |
|-----------|--------------|-------|--------|
| TCP Connect (-p-) | No | Very slow | Full 3-way handshake |
| SYN Scan (-sS) | Yes | Fast | Half-open, no handshake |
| UDP Scan (-sU) | Yes | Slow | No connection state |

### Attempt 3 — Aggressive Scan Default
Command: nmap -A 192.168.1.139
Result: Note: Host seems down. If it is really up, but blocking our ping probes, try -Pn. Nmap done: 0 hosts up.
Analysis: Host blocking ICMP ping probes.
nmap gives false negative — host is alive but stealthy.
Firewall dropping all ICMP packets at L3.
Lesson: Always use -Pn on suspected ICMP-blocking hosts.

### Attempt 4 — Ping Skip Scan
Command: nmap -Pn 192.168.1.139
Result:
Host is up (0.21s latency)
907 filtered tcp ports (no-response)
93 filtered tcp ports (host-unreach)
All 1000 scanned ports: ignored

Analysis:
Host IS alive confirmed by 0.21s latency.
All 1000 common ports filtered = heavy firewall active.
host-unreach on 93 ports = router actively rejecting.
No open ports found in top 1000.

### Attempt 5 — Netcat Port Testing
Commands:
nc -zv 192.168.1.1 80
nc -zv 192.168.1.1 443
nc -zv 192.168.1.139 22
nc -zv 192.168.1.139 80

| Target | Port | Service | Result | Meaning |
|--------|------|---------|--------|---------|
| 192.168.1.1 | 80 | HTTP | Connected | Router HTTP open |
| 192.168.1.1 | 443 | HTTPS | Connected | Router HTTPS open |
| 192.168.1.139 | 22 | SSH | No route | SSH blocked/closed |
| 192.168.1.139 | 80 | HTTP | No route | HTTP blocked/closed |

Key Finding: Router ports confirmed open via netcat.
Unknown host actively rejecting all tested connections.
netcat operates at L4 — confirms transport layer behavior.

### Attempt 6 — DNS Reverse Lookup
Commands:
dig ANY 192.168.1.139
nslookup 192.168.1.139

dig Result: status NXDOMAIN, SERVER 8.8.8.8#53 (TCP), Query time 280ms
nslookup Result: server can't find 139.1.168.192.in-addr.arpa: NXDOMAIN

Analysis:
No PTR record exists for 192.168.1.139.
Private IP range — no public DNS expected.
Device not registered with any DNS server.
dig used TCP not UDP default — response exceeded 512 bytes
triggering automatic TCP fallback. This is a finding:
dig layer = L7, protocol switched TCP/53.

### Attempt 7 — Default Script Scan
Command: nmap -sV --script=default 192.168.1.139
Result: Note: Host seems down. Nmap done: 0 hosts up.
Analysis: Without -Pn nmap gives up on ICMP-blocking hosts.
Confirmed: always add -Pn on hosts that block ICMP.

### Unknown Host — Complete Profile
| Property | Finding | Confidence |
|----------|---------|------------|
| IP | 192.168.1.139 | Confirmed |
| Status | Alive | High (0.21s latency) |
| ICMP | Blocked | High |
| Top 1000 ports | All filtered | High |
| OS | Unknown | Cannot determine (no root) |
| DNS name | None | Confirmed NXDOMAIN |
| SSH port 22 | No route | High |
| HTTP port 80 | No route | High |
| Identity | Unknown | Unresolved |

### Most Likely Device Identity
| Possibility | Evidence For | Evidence Against |
|------------|-------------|-----------------|
| Smartphone | Common on home networks | No open ports typical |
| IoT device | Filtered ports = locked down | No service fingerprint |
| Smart TV | Often blocks ICMP | Cannot confirm |
| Attacker device | Stealth behavior | No aggressive activity seen |

Recommended action: Check router DHCP table at
http://192.168.1.1 connected devices section.
Match 192.168.1.139 to MAC address and device name.

---

## 8. Phase 5 — Port 80 Reappearance Analysis

### Finding
Port 80 was closed in Lab 002. Reappeared in this session.

### HTTP Banner Extracted by nmap
HTTP/1.0 302 Redirect
Server: Demo-Webs
Location: http://192.168.1.1/index.html
X-Frame-Options: SAMEORIGIN
Pragma: no-cache
Cache-Control: no-cache

### HTTP Header Security Analysis
| Header | Value | Security Meaning |
|--------|-------|-----------------|
| Server | Demo-Webs | OEM web server identity exposed |
| HTTP version | 1.0 | Old protocol — older firmware |
| 302 Redirect | to index.html | Admin panel redirect confirmed |
| X-Frame-Options | SAMEORIGIN | Clickjacking protection present |
| Pragma no-cache | no-cache | Prevents credential caching |
| Cache-Control | no-cache | Prevents credential caching |

### Why Port 80 Reappeared
| Cause | Likelihood |
|-------|-----------|
| Router rebooted, reset to default | High |
| HTTP disable not saved before exit | High |
| ZLT T30 PLUS re-enables HTTP on reboot | Medium |

Action required: Re-disable HTTP in router admin panel.
Verify setting persists after manual router reboot.

---

## 9. Complete Findings Summary

| ID | Finding | Severity | Layer | Recommendation |
|----|---------|----------|-------|----------------|
| F-01 | Port 80 HTTP re-enabled | HIGH | L7 | Disable and verify persistence |
| F-02 | Unknown host 192.168.1.139 | MEDIUM | L3 | Identify via DHCP table |
| F-03 | 192.168.1.139 blocks ICMP | INFO | L3 | Use -Pn for future scans |
| F-04 | netstat blocked no root | INFO | L4 | Root needed for socket enum |
| F-05 | OS scan requires root | INFO | L3 | Root needed for -O flag |
| F-06 | Full port scan too slow | INFO | L4 | Root or PC needed for -p- |
| F-07 | DNS version still exposed | MEDIUM | L7 | Block CHAOS queries |
| F-08 | Telnet available on device | MEDIUM | L7 | Never use on live networks |

---

## 10. OSI Layer Mapping — All Findings

| Layer | Finding | Attack Vector | Status |
|-------|---------|--------------|--------|
| L7 Application | Port 80 HTTP re-enabled | Credential interception | HIGH |
| L7 Application | DNS version disclosure | CVE targeting | WARNING |
| L7 Application | Telnet available | Plaintext credential capture | WARNING |
| L7 Application | dig used TCP fallback | DNS amplification possible | INFO |
| L4 Transport | netstat blocked | No socket visibility | INFO |
| L4 Transport | 192.168.1.139 all ports filtered | Port scan evasion | MEDIUM |
| L3 Network | 192.168.1.139 blocks ICMP | Host discovery evasion | MEDIUM |
| L3 Network | OS fingerprint blocked | No root = blind scan | INFO |
| L2 Data Link | ARP poisoning possible on LAN | MITM attack vector | WARNING |
| L1 Physical | ZLT T30 PLUS hardware | Physical access risk | INFO |

---

## 11. Limitations

| Limitation | Cause | Impact |
|------------|-------|--------|
| No OS fingerprinting | No root (-O needs raw packets) | Cannot ID unknown host OS |
| Full port scan impractical | No SYN scan without root | 2+ hours for -p- on mobile |
| netstat blocked | Android kernel restriction | No socket table visibility |
| Unknown host unidentified | All ports filtered, no DNS | Identity unresolved |
| No packet capture | No root (tcpdump needs root) | Cannot see traffic content |
| Wi-Fi scan throttled | Android 11 restriction | Partial network visibility |

---

## 12. Commands Reference

OSI Drilling Commands:
ping -c 3 192.168.1.1             L3 ICMP
dig google.com                     L7 UDP/53
nmap -sn 192.168.1.0/24           L3 ICMP ping sweep
ifconfig                           L2 Ethernet MAC display
netstat -tulnp                     L4 TCP/UDP blocked no-root

Unknown Host Enumeration:
nmap -sV -sC -O 192.168.1.139     OS scan requires root
nmap -p- 192.168.1.139            Full 65535 port scan slow
nmap -A 192.168.1.139             Aggressive ICMP blocked
nmap -Pn 192.168.1.139            Skip ping scan anyway
nmap -sV --script=default 192.168.1.139  Default scripts

Port Connectivity Testing netcat:
nc -zv 192.168.1.1 80             Test router HTTP L4
nc -zv 192.168.1.1 443            Test router HTTPS L4
nc -zv 192.168.1.139 22           Test unknown host SSH L4
nc -zv 192.168.1.139 80           Test unknown host HTTP L4

DNS Reconnaissance:
dig ANY 192.168.1.139              DNS any-record query L7
nslookup 192.168.1.139             Reverse DNS lookup L7
dig -x 192.168.1.139               PTR record query L7

Telnet Test:
telnet                             Opens interactive prompt L7
telnet 192.168.1.1 80             Connect to specific port

Router Service Scan:
nmap -sV 192.168.1.1              Service versions L4/L7
nmap -A 192.168.1.1               Aggressive SSL cert L3-L7
nmap -sV --script=http-title 192.168.1.1  HTTP title grab

---

## 13. Conclusions

This session produced three major outcomes:

1. OSI Misconceptions Corrected
Six protocol/layer mapping errors identified and corrected.
Most critical: ping=ICMP not IP, dig=UDP not TCP,
nmap -sn=L3 not L4, ifconfig=L2 not L1, netstat=L4 not L2.
These are standard interview questions. Now corrected permanently.

2. Unknown Host Partially Enumerated
192.168.1.139 confirmed alive but unidentified.
Heavy firewall, no open ports, no DNS record, ICMP blocked.
Root access would enable OS fingerprinting and faster
port scanning to complete identification.
DHCP table check on router is the fastest resolution path.

3. Router Hardening Not Persistent
Port 80 reappeared after previous session disable.
ZLT T30 PLUS likely resets HTTP on reboot.
Persistent hardening requires firmware-level config save
and post-reboot verification scan.

Methodology Validation:
OODA loop applied consistently throughout.
Predict then Execute then Correct then Document.
Each failed attempt produced actionable intelligence.
No wasted effort — every error became a learning artifact.

---

All testing performed on analyst-owned equipment.
No unauthorized systems were accessed.
Report format: Professional penetration test writeup.

