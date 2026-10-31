# Lab 5 - Static Code Analysis Issues

## 1. Issues Identified

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Shell command injection risk | Security - High | 25 | subprocess.run() uses shell=True with string concatenation. | Pass command arguments as a list and remove shell=True. |
| SQL injection risk | Security - Medium | 9 | SQL query uses an f-string to insert user input directly. | Use parameterized SQL queries. |
| Bare except clause | Code Quality | 31 | Catches every exception without specifying its type. | Catch an appropriate specific exception. |
| File handling without context manager | Code Quality | 18-20 | File may not close properly if an error occurs. | Use a with statement. |
| Missing encoding | Code Quality | 18 | File is opened without explicitly specifying encoding. | Specify UTF-8 encoding. |
| Unused argument | Code Quality | 13 | driver parameter is never used. | Remove the unused parameter. |
| Naming convention violations | Code Quality | 8, 13, 17, 24, 28 | Function names use camelCase instead of snake_case. | Rename functions using snake_case. |
| Missing documentation | Code Quality | Multiple | Module and functions lack docstrings. | Add module and function docstrings. |
| Long lines | Formatting | 5, 9, 13, 30 | Lines exceed recommended length. | Split long statements across multiple lines. |
| Missing final newline | Formatting | End of file | File does not end with a newline. | Add a final newline. |
| Assert used for runtime validation | Security / Reliability | 39 | Bandit reports use of assert for validation. | Replace with an explicit conditional check. |

## 2. Analysis Tools

- Pylint: 3.67/10
- Bandit: 4 findings (1 High, 1 Medium, 2 Low)
- Flake8: 6 violations

## 3. Conclusion

Static code analysis identified security vulnerabilities, code-quality problems, naming convention violations and formatting issues. These findings will be addressed in the improved implementation.
