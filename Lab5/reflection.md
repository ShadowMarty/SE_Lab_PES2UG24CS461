# Reflection: Static Code Analysis

### Q1: What are the key differences between the findings reported by Pylint, Flake8, and Bandit?
Each tool checks a different part of the code. Flake8 checks for style, formatting, and PEP 8 rules like line length, spacing after commas, and blank lines. Pylint is a deeper code quality checker that looks at code design, unused variables, missing docstrings, and bad practices like not using 'with' when opening files. Bandit is purely a security scanner that finds vulnerabilities like SQL injection, unsafe shell commands, and insecure imports.

### Q2: Why are vulnerabilities like SQL injection and Command Injection particularly critical in real-world systems?
Both vulnerabilities let untrusted user inputs run as code. With SQL injection, an attacker can steal private student records, change fees, or delete whole database tables. With Command injection (using shell=True), an attacker can run any command they want on the server's operating system, which can let them take full control of the machine.

### Q3: How does adopting static analysis early in the Software Development Life Cycle (SDLC) benefit software teams?
Fixing bugs early while writing code is much easier and cheaper than fixing them after the app goes live. It also keeps code clean and readable across the entire team, and avoids spending time in code reviews arguing about simple formatting rules.

### Q4: What challenges might a development team encounter when introducing static analysis to a legacy codebase, and how can they be mitigated?
If you run these tools on old code, they can show hundreds or thousands of errors at once, which can overwhelm developers. Also, some warnings might be false alarms. A good way to handle this is to only check new and modified files first, and slowly clean up older parts. Teams can also configure the rules file to turn off rules that are not relevant to their project.
