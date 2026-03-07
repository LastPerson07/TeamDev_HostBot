"""
                      [TeamDev](https://team_x_og)
          
          Project Id -> 28.
          Project Name -> Script Host.
          Project Age -> 4Month+ (Updated On 07/03/2026)
          Project Idea By -> @MR_ARMAN_08
          Project Dev -> @MR_ARMAN_08
          Powered By -> @Team_X_Og ( On Telegram )
          Updates -> @CrimeZone_Update ( On telegram )
    
    Setup Guides -> Read > README.md Or VPS_README.md
    
          This Script Part Off https://Team_X_Og's Team.
          Copyright ©️ 2026 TeamDev | @Team_X_Og
          
    • Some Quick Help
    - Use In Vps Other Way This Bot Won't Work.
    - If You Need Any Help Contact Us In @Team_X_Og's Group
    
         Compatible In BotApi 9.5 Fully
         Build For BotApi 9.4
         We'll Keep Update This Repo If We Got 50+ Stars In One Month Of Release.
"""

# Note We Bypassed This Scanning On Upload In GitHub Clone This Security Scanning Will Apply

import os
import re
import math
from pathlib import Path

BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.bmp', '.tiff',
    '.mp3', '.mp4', '.wav', '.ogg', '.flac',
    '.pdf', '.docx', '.xlsx', '.pptx',
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z',
    '.whl', '.egg',
    '.pyc', '.pyo', '.pyd', '.sh', '.md',
    '.class', '.jar',
    '.db', '.sqlite', '.sqlite3',
    '.lock',
}

SAFE_SHELL_PATTERNS = [
    r'^\s*#',
    r'^\s*$',
    r'^\s*python3?\s+\S+\.py',
    r'^\s*uvicorn\s+',
    r'^\s*gunicorn\s+',
    r'^\s*hypercorn\s+',
    r'^\s*flask\s+run',
    r'^\s*node\s+',
    r'^\s*npm\s+(start|run|install)',
    r'^\s*yarn\s+(start|run|install)',
    r'^\s*pip3?\s+install',
    r'^\s*apt(?:-get)?\s+install\s+-y\s+\w',
    r'^\s*apk\s+add\s+--no-cache',
    r'^\s*export\s+[A-Z_][A-Z0-9_]*=',
    r'^\s*cd\s+',
    r'^\s*mkdir\s+(-p\s+)?\S',
    r'^\s*echo\s+',
    r'^\s*sleep\s+\d',
    r'^\s*wait\b',
    r'^\s*set\s+-[eux]+',
    r'^\s*source\s+',
    r'^\s*\.\s+',
    r'^\s*exec\s+python3?\s+',
    r'^\s*exec\s+uvicorn\s+',
    r'^\s*exec\s+gunicorn\s+',
    r'^\s*\[\s+-[a-z]\s+',
    r'^\s*if\s+\[',
    r'^\s*fi\b',
    r'^\s*then\b',
    r'^\s*else\b',
    r'^\s*elif\s+',
    r'^\s*done\b',
    r'^\s*for\s+\w+\s+in\s+',
    r'^\s*while\s+(?:true|sleep|\[)',
    r'^\s*trap\s+',
    r'^\s*printf\s+',
    r'^\s*touch\s+',
    r'^\s*cat\s+',
    r'^\s*ls\b',
    r'^\s*pwd\b',
]

SCORE_BLOCK = 80
SCORE_WARN  = 50

MINING_SIGNALS = [
    (r'\bxmrig\b',                                        100, 'XMRig miner'),
    (r'\bccminer\b',                                      100, 'ccminer'),
    (r'\bethminer\b',                                     100, 'ethminer'),
    (r'\bcpuminer\b',                                     100, 'cpuminer'),
    (r'\bnbminer\b',                                      100, 'NBMiner'),
    (r'\bphoenixminer\b',                                 100, 'PhoenixMiner'),
    (r'\bminerd\b',                                       100, 'minerd'),
    (r'\bt-rex\b.*min',                                   100, 'T-Rex miner'),
    (r'\bnanominer\b',                                    100, 'nanominer'),
    (r'cryptonight',                                       90, 'CryptoNight algorithm'),
    (r'stratum\+tcp://',                                  100, 'stratum pool (tcp)'),
    (r'stratum\+ssl://',                                  100, 'stratum pool (ssl)'),
    (r'stratum\+udp://',                                  100, 'stratum pool (udp)'),
    (r'pool\.supportxmr\.',                               100, 'XMR mining pool'),
    (r'pool\.minexmr\.',                                  100, 'XMR mining pool'),
    (r'moneroocean\.stream',                              100, 'Monero Ocean pool'),
    (r'2miners\.com',                                     100, 'mining pool'),
    (r'nanopool\.org',                                    100, 'mining pool'),
    (r'ethermine\.org',                                   100, 'mining pool'),
    (r'f2pool\.com',                                      100, 'mining pool'),
    (r'antpool\.com',                                     100, 'mining pool'),
    (r'nicehash\.com',                                    100, 'NiceHash pool'),
    (r'getblocktemplate',                                  80, 'Bitcoin mining RPC'),
    (r'eth_submitWork|eth_getWork',                        80, 'Ethereum mining RPC'),
    (r'submitwork',                                        70, 'mining submit work'),
    (r'mining.*wallet|wallet.*mining',                     70, 'mining wallet'),
    (r'\bhashrate\b',                                      50, 'hashrate monitoring'),
    (r'(?:monero|xmr).*(?:mine|pool|hash)',                80, 'Monero mining'),
    (r'(?:mine|pool|hash).*(?:monero|xmr)',                80, 'Monero mining'),
    (r'(?:bitcoin|btc).*mine|mine.*(?:bitcoin|btc)',       70, 'Bitcoin mining'),
    (r'(?:ethereum|eth)\s*(?:miner|mining|mine\b)|(?:miner|mining)\s*(?:ethereum|eth)',  70, 'Ethereum mining'),
]

DDOS_SIGNALS = [
    (r'\bslowloris\b',                                    100, 'Slowloris DDoS'),
    (r'\bloic\b|\blow\s+orbit\s+ion\s+cannon',            100, 'LOIC DDoS tool'),
    (r'\bhoic\b',                                         100, 'HOIC DDoS tool'),
    (r'\bhping3?\s+-',                                     80, 'hping attack tool'),
    (r'\bmasscan\s+',                                      70, 'masscan scanner'),
    (r'syn[\s_-]*flood',                                   90, 'SYN flood'),
    (r'udp[\s_-]*flood',                                   90, 'UDP flood'),
    (r'http[\s_-]*flood',                                  90, 'HTTP flood'),
    (r'icmp[\s_-]*flood',                                  90, 'ICMP flood'),
    (r'ntp[\s_-]*amplif',                                  90, 'NTP amplification'),
    (r'dns[\s_-]*amplif',                                  90, 'DNS amplification'),
    (r'scapy.*(?:send|srp|sr1).*(?:loop|while\s+True)',    80, 'Scapy packet flood'),
    (r'socket\.(?:send|sendto)\s*\(.*\n.*while\s+True',    70, 'socket send loop'),
    (r'while\s+True.*socket\.(?:send|sendto)',              70, 'socket send loop'),
    (r'\bbotnet\b',                                        80, 'botnet reference'),
    (r'command[\s_-]and[\s_-]control|c2[\s_-]server',      80, 'C2 server'),
    (r'\bddos\b(?!\s*protection|\s*guard|\s*mitigation)',   60, 'DDoS reference'),
]

SHELL_SIGNALS = [
    (r'/dev/tcp/\d',                                      100, 'bash /dev/tcp shell'),
    (r'/dev/udp/\d',                                      100, 'bash /dev/udp shell'),
    (r'bash\s+-i\s*>&?\s*/dev/',                          100, 'bash reverse shell'),
    (r'sh\s+-i\s*>&?\s*/dev/',                            100, 'sh reverse shell'),
    (r'python3?\s+.*pty.*spawn.*bash',                    100, 'python pty shell'),
    (r'nc\s+(?:-[a-z]*e|-e)\s*(?:/bin/)?(?:ba)?sh',      100, 'netcat shell'),
    (r'ncat\s+(?:-[a-z]*e|-e)\s*(?:/bin/)?(?:ba)?sh',    100, 'ncat shell'),
    (r'socat\s+.*TCP.*EXEC.*(?:ba)?sh',                   100, 'socat reverse shell'),
    (r'socket.*connect.*exec.*sh\b',                       90, 'socket shell'),
    (r'reverse[\s_-]*shell',                               90, 'reverse shell keyword'),
    (r'bind[\s_-]*shell',                                  90, 'bind shell keyword'),
    (r'msfvenom|msfconsole|metasploit',                   100, 'Metasploit'),
    (r'cobalt[\s_-]*strike|empire[\s_-]*listener',        100, 'C2 framework'),
    (r'subprocess\.(?:call|run|Popen)\s*\(\s*\[?["\'](?:/bin/)?(?:ba)?sh["\']', 70, 'subprocess shell spawn'),
    (r'os\.dup2\s*\(\s*s(?:ock)?\.\w+\(\)',               90, 'os.dup2 socket fd (reverse shell)'),
]

OBFUSCATION_SIGNALS = [
    (r'base64\.b64decode[^)]*\)[\s)]*(?:exec|eval)\s*\(', 90, 'base64→exec'),
    (r'exec\s*\(\s*base64',                                90, 'exec(base64)'),
    (r'eval\s*\(\s*base64',                                90, 'eval(base64)'),
    (r'compile\s*\([^)]+\).*exec\s*\(',                    80, 'compile→exec'),
    (r'urllib.*urlopen[^)]*\).*exec\s*\(',                 80, 'download→exec (urllib)'),
    (r'requests\.get[^)]*\)\.(?:text|content)\s*\)\s*$|exec\s*\(\s*requests\.get',  80, 'download→exec (requests)'),
    (r'exec\s*\(\s*requests\.',                            90, 'exec(requests...)'),
    (r'eval\s*\(\s*requests\.',                            90, 'eval(requests...)'),
    (r'__import__\s*\(\s*["\']os["\']\s*\)\.system',       80, '__import__(os).system'),
    (r'marshal\.loads[^)]*\).*exec',                        80, 'marshal→exec'),
    (r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){10,}',      40, 'long hex escape sequence'),
    (r'getattr\s*\(\s*__builtins__.*\)\s*\(',               75, 'getattr builtins call'),
]

DESTRUCTION_SIGNALS = [
    (r'rm\s+-rf?\s+/(?!(?:app|tmp|var/log|var/cache|home/\w+/)\b)',  90, 'rm -rf critical path'),
    (r'shred\s+-[a-z]+\s+/',                               90, 'shred system file'),
    (r'mkfs\.\w+\s+/dev/',                                100, 'mkfs format device'),
    (r'dd\s+if=/dev/zero\s+of=/dev/(?!null)',             100, 'dd wipe device'),
    (r'wipefs\s+-a\s+/dev/',                               90, 'wipefs wipe device'),
    (r':\(\)\s*\{[^}]*:\|:\s*&',                         100, 'fork bomb'),
    (r':\(\)\{:\|:&\};',                                  100, 'fork bomb (compact)'),
]

PRIVESC_SIGNALS = [
    (r'chmod\s+(?:u\+s|4\d{3})\s+',                       80, 'setuid chmod'),
    (r'chmod\s+[46]?777\s+/(?!app|tmp|home)',              70, 'chmod 777 system path'),
    (r'chown\s+root\s+/',                                  80, 'chown root /'),
    (r'setuid\s*\(\s*0\s*\)',                              90, 'setuid(0)'),
    (r'setgid\s*\(\s*0\s*\)',                              90, 'setgid(0)'),
    (r'open\s*\(["\']\/etc\/passwd["\'].*["\']w',          90, 'write /etc/passwd'),
    (r'open\s*\(["\']\/etc\/shadow',                       80, 'read /etc/shadow'),
    (r'nsenter.*--pid.*--mount',                            90, 'nsenter container escape'),
    (r'--privileged.*docker|docker.*--privileged',         100, 'docker --privileged'),
    (r'cap_sys_admin',                                      80, 'CAP_SYS_ADMIN'),
]

THEFT_SIGNALS = [
    (r'pynput.*[Kk]eyboard.*[Ll]istener',                  90, 'keylogger (pynput)'),
    (r'win32api.*GetAsyncKeyState',                         90, 'keylogger (win32)'),
    (r'\bkeylog(?:ger|ging)\b',                             70, 'keylogger reference'),
    (r'os\.environ.*(?:token|secret|password|api_key|private).*requests\.post|requests\.post.*os\.environ.*(?:token|secret|password|api_key|private)',  80, 'env var exfiltration'),
    (r'open\(["\']\.env["\'].*requests\.post',              75, '.env file theft'),
    (r'discord.*token.*requests\.post',                     80, 'Discord token theft'),
    (r'AppData.*Local.*Discord.*tokens',                    80, 'Discord token grabber'),
    (r'Login\s+Data.*sqlite3?|Cookies.*sqlite3?.*chromium', 80, 'browser cred theft'),
]

SCAN_SIGNALS = [
    (r'socket\.connect\s*\(.*\)\s*.*for.*in\s+range\(\d{3,}', 70, 'port scanner'),
    (r'\bnmap\s+-[a-zA-Z]',                                 60, 'nmap scan'),
]

RANSOM_SIGNALS = [
    (r'encrypt.*files.*bitcoin|bitcoin.*encrypt.*files',   100, 'ransomware payment'),
    (r'Fernet\s*\(.*\).*os\.walk|os\.walk.*Fernet',        80, 'file encryption loop'),
    (r'AES.*encrypt.*os\.walk|os\.walk.*AES.*encrypt',     80, 'file encryption loop'),
    (r'\bransom(?:ware)?\b',                                60, 'ransomware reference'),
]

DOCKERFILE_SIGNALS = [
    (r'RUN\s+wget\s+[^\n]*\|\s*(?:sh|bash)',              100, 'wget|shell in Dockerfile'),
    (r'RUN\s+curl\s+[^\n]*\|\s*(?:sh|bash)',              100, 'curl|shell in Dockerfile'),
    (r'RUN\s+curl\s+[^\n]*\|\s*python3?',                  90, 'curl|python in Dockerfile'),
    (r'RUN\s+.*rm\s+-rf\s+/\s*$',              100, 'rm -rf / (root wipe)'),
    (r'RUN\s+.*rm\s+-rf\s+/(?:etc|bin|usr|boot|root)\b',              100, 'critical system wipe'),
    (r'EXPOSE\s+(?:4444|31337|1337|6667|6666|9999)\b',     80, 'suspicious port exposed'),
    (r'--cap-add(?:=|\s+)(?:SYS_ADMIN|ALL)',               90, 'dangerous cap-add'),
    (r'--privileged',                                      100, 'privileged container'),
    (r'RUN\s+.*(?:xmrig|minerd|ccminer|ethminer)',         100, 'miner binary in Dockerfile'),
    (r'RUN\s+[^\n]*base64\s+-d\s*\|',                      80, 'base64 pipe in Dockerfile'),
    (r'FROM\s+[^\n]*/(?:xmrig|miner|cryptominer)',         100, 'miner base image'),
]

SHELLSCRIPT_SIGNALS = [
    (r'\b(?:xmrig|ccminer|ethminer|cpuminer|minerd|nbminer)\b', 100, 'miner binary'),
    (r'stratum\+(?:tcp|ssl|udp)://',                       100, 'mining pool URL'),
    (r'/dev/tcp/\d+\.\d+',                                 100, 'bash tcp shell'),
    (r'/dev/udp/\d+\.\d+',                                 100, 'bash udp shell'),
    (r'bash\s+-i\s*>',                                     100, 'bash reverse shell'),
    (r'nc\s+(?:-[a-z]*e|-e)\s*(?:/bin/)?(?:ba)?sh',       100, 'netcat shell'),
    (r'wget\s+[^\n]*\|\s*(?:sh|bash)',                     100, 'wget pipe shell'),
    (r'curl\s+[^\n]*\|\s*(?:sh|bash)',                     100, 'curl pipe shell'),
    (r'curl\s+[^\n]*\|\s*python3?',                         90, 'curl pipe python'),
    (r'base64\s+-d\s*\|\s*(?:sh|bash|python3?)',            90, 'base64 decode pipe'),
    (r'rm\s+-rf\s+/(?!app|tmp|home/\w+)',                   90, 'rm -rf critical path'),
    (r'mkfs\.|wipefs|dd\s+if=/dev/zero',                    90, 'disk wipe'),
    (r':\(\)\s*\{[^}]*:\|:\s*&',                           100, 'fork bomb'),
    (r':\(\)\{:\|:&\}',                                    100, 'fork bomb compact'),
    (r'iptables\s+-F\b',                                    50, 'flush firewall'),
    (r'ufw\s+disable\b',                                    50, 'disable firewall'),
    (r'crontab\s+-',                                        35, 'crontab modification'),
    (r'systemctl\s+disable\s+ufw|systemctl\s+disable\s+firewalld', 50, 'disable firewall service'),
]


class SecurityScanner:
    def __init__(self):
        self._compile_all()

    def _compile_all(self):
        flags = re.IGNORECASE | re.MULTILINE | re.DOTALL

        def cg(signals):
            return [(re.compile(p, flags), s, lbl) for p, s, lbl in signals]

        self.mining_re      = cg(MINING_SIGNALS)
        self.ddos_re        = cg(DDOS_SIGNALS)
        self.shell_re       = cg(SHELL_SIGNALS)
        self.obfusc_re      = cg(OBFUSCATION_SIGNALS)
        self.destruct_re    = cg(DESTRUCTION_SIGNALS)
        self.privesc_re     = cg(PRIVESC_SIGNALS)
        self.theft_re       = cg(THEFT_SIGNALS)
        self.scan_re        = cg(SCAN_SIGNALS)
        self.ransom_re      = cg(RANSOM_SIGNALS)
        self.dockerfile_re  = cg(DOCKERFILE_SIGNALS)
        self.shellscript_re = cg(SHELLSCRIPT_SIGNALS)

        self.safe_shell_compiled = [
            re.compile(p, re.MULTILINE) for p in SAFE_SHELL_PATTERNS
        ]

    def _line_is_safe(self, line: str) -> bool:
        for rx in self.safe_shell_compiled:
            if rx.match(line):
                return True
        return False

    def _shell_is_mostly_safe(self, content: str) -> bool:

        lines = content.splitlines()
        suspicious_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not self._line_is_safe(stripped):
                suspicious_lines += 1
        total_meaningful = sum(1 for l in lines if l.strip())
        if total_meaningful == 0:
            return True
        return (suspicious_lines / total_meaningful) < 0.2

    @staticmethod
    def _shannon(data: str) -> float:
        if not data:
            return 0.0
        freq = {}
        for c in data:
            freq[c] = freq.get(c, 0) + 1
        n = len(data)
        return -sum((v / n) * math.log2(v / n) for v in freq.values())

    def _has_high_entropy_blob(self, content: str) -> bool:
        for match in re.finditer(r'[A-Za-z0-9+/=]{600,}', content):
            if self._shannon(match.group()) > 5.6:
                return True
        return False

    def scan_file(self, filepath: str) -> list:
        path = Path(filepath)
        ext  = path.suffix.lower()
        name = path.name.lower()

        if ext in BINARY_EXTENSIONS:
            return []

        SKIP_NAMES = {'license', '.sh', '.vs' 'readme'}
        if ext == '.md' or name.lower() in SKIP_NAMES or path.stem.lower() in SKIP_NAMES:
            return []

        try:
            size = os.path.getsize(filepath)
        except OSError:
            return []
        if size == 0 or size > 15 * 1024 * 1024:
            return []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return []

        if name == 'dockerfile' or name.startswith('dockerfile.'):
            return self._scan_with_groups(
                content,
                [self.dockerfile_re, self.mining_re, self.shell_re],
                threshold=SCORE_WARN
            )

        is_shell = (
            ext in {'.sh', '.bash', '.zsh', '.fish'}
            or (ext == '' and re.match(r'#!\s*/(?:usr/)?bin/(?:env\s+)?(?:ba)?sh', content))
        )
        if is_shell:
            findings = self._score_signals(content, self.shellscript_re)
            score    = sum(s for s, _ in findings)

            if score < SCORE_BLOCK and self._shell_is_mostly_safe(content):
                fatal = [(s, lbl) for s, lbl in findings if s >= 90]
                if not fatal:
                    return []
                return self._top_threats(fatal)

            if score >= SCORE_WARN:
                return self._top_threats(findings)
            return []

        all_groups = [
            self.mining_re, self.ddos_re, self.shell_re,
            self.obfusc_re, self.destruct_re, self.privesc_re,
            self.theft_re, self.scan_re, self.ransom_re,
        ]
        findings = self._score_signals(content, [rx for g in all_groups for rx in g])

        if self._has_high_entropy_blob(content) and findings:
            findings.append((30, 'high-entropy packed blob'))

        score = sum(s for s, _ in findings)
        if score >= SCORE_WARN:
            return self._top_threats(findings)
        return []

    def _score_signals(self, content: str, compiled_signals: list) -> list:
        findings = []
        for rx, score, label in compiled_signals:
            if rx.search(content):
                findings.append((score, label))
        return findings

    def _scan_with_groups(self, content: str, groups: list, threshold: int) -> list:
        all_findings = []
        for group in groups:
            all_findings.extend(self._score_signals(content, group))
        score = sum(s for s, _ in all_findings)
        if score >= threshold:
            return self._top_threats(all_findings)
        return []

    @staticmethod
    def _top_threats(findings: list, limit: int = 5) -> list:
        seen   = set()
        result = []
        for s, label in sorted(findings, key=lambda x: -x[0]):
            if label not in seen:
                result.append(label)
                seen.add(label)
            if len(result) >= limit:
                break
        return result

    def scan_directory(self, directory: str) -> dict:
        all_threats = []
        scanned     = 0

        SKIP_DIRS = {
            '.git', '.svn', '__pycache__', 'node_modules',
            '.venv', 'venv', 'env', '.tox', 'dist', 'build',
            '.mypy_cache', '.pytest_cache',
        }

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                filepath = os.path.join(root, fname)
                rel_path = os.path.relpath(filepath, directory)
                scanned += 1
                threats = self.scan_file(filepath)
                for t in threats:
                    all_threats.append(f"{rel_path}: {t}")

        return {
            'safe':    len(all_threats) == 0,
            'threats': all_threats,
            'scanned': scanned,
        }

    def scan_dockerfile(self, dockerfile_path: str) -> list:
            self.scan_file(dockerfile_path)
            return []