\# Lab 5 – Reflection on Static Code Analysis



\## 1. What problems were identified in the original code?



The original school transport program contained several security and code-quality issues. These included SQL injection caused by f-string queries, shell command injection due to `subprocess.run()` with `shell=True`, a bare except clause, missing file encoding, improper file handling, unused arguments, naming convention violations, missing docstrings, long lines and the use of assert for runtime validation.



\## 2. How were the identified problems fixed?



The SQL queries were changed to use parameterized queries. The subprocess shell command was removed and replaced with Python's print function. File handling was improved using a context manager with UTF-8 encoding. Function names were changed to snake\_case, docstrings were added, and the bare exception and assert statements were removed. Long lines and formatting issues were also corrected.



\## 3. What improvements were observed after applying static code analysis?



The Pylint score improved from 3.67/10 to 10/10. Bandit findings decreased from four security issues to zero. Flake8 violations decreased from six to zero. These results demonstrate improved code quality, readability, formatting and security.



\## 4. What did you learn from this lab?



I learned how static code analysis tools such as Pylint, Bandit and Flake8 help identify programming mistakes, security vulnerabilities and coding-standard violations. I also understood the importance of secure SQL queries, safe file handling, proper exception handling and following Python coding conventions.



