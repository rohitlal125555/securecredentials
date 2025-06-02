# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/).

--- 

## Planned Changes for Upcoming Releases

- Shell CLI for direct interaction with the package.
- YAML configuration support for easier setup and management.
- Test cases for the `securecredentials` package to ensure reliability and correctness.
- Batch export/import credentials in plaintext for easy migration or backup.
- Delete individual key-value pairs from the database.
- Move logging from `core` to `helper` library for better modularity.
- Any bug-fixes or GitHub issues.

---
## [2.1] - 2025-06-02

This version introduces design changes focused on improving encryption flexibility and security.

⚠️ Note: This release is not backward compatible.

For migration from 2.0 to 2.1, you'll need to recreate the master key and re-encrypt your secrets.

### 🆕 Added
- Introduced passphrase-based key derivation as an alternative to system-bound encryption.
- Added `clear_database()` method to easily reset stored `user` and `master` databases without manually deleting files.
- Implemented lazy initialization to support optional passphrase input during package setup.
- Added custom exception classes for better error handling, including: 
`MasterKeyDecryptionError`, `FieldDecryptionError`, `PassphraseNotAllowedError` and other specialized exceptions to improve code clarity and debugging.

### 🛠️ Changed
- Migrated from `PBKDF2HMAC` to `Scrypt` as the Key Derivation Function to improve resistance against GPU-based attacks.
- Updated encrypted master key storage format from binary blob to JSON for better extensibility.
- `_load_master_key()` now raises an exception if the master key is missing, instead of logging a warning. This change improves safety under the new lazy initialization model by preventing silent failures.


### 🐞 Fixed
- Normalized system environment variables by lowercasing and stripping whitespace to ensure consistent key derivation.

---

## [2.0] - 2025-05-20

This release introduces major design changes focused on improving encryption security.

⚠️ Note: This release is not backward compatible.

To migrate from v1.x to v2.x, you must regenerate the master key and re-encrypt all secrets.
Please raise a GitHub issue if you run into any issues during migration.

### 🆕 Added
- Upgraded encryption to AES-GCM (256-bit) for stronger, authenticated encryption.
- Introduced a dual encryption scheme: master keys are now encrypted using deterministic keys derived via PBKDF2HMAC from system variables.
- Implemented schema versioning for both user data and master key databases. 

### 🛠️ Changed
- Replaced Fernet (128-bit) with stronger AES-GCM encryption.
- The master key is no longer stored in plaintext on disk


---

## [1.3.3] - 2025-05-01
### 🆕 Added
- Support for ANSI escape codes in Windows command prompt for improved terminal readability.

---

## [1.3.2] - 2025-04-22
### 🐞 Fixed
- Minor bug fixes in the help() function output formatting.


---

## [1.3.1] - 2025-04-19

This update introduces a dynamic module interface for easier imports, while maintaining backward compatibility.

### 🆕 Added
- Dynamic module-level interface to simplify imports and improve usability.
- Internal libraries were streamlined for better maintainability.

---

## [1.1] - 2025-01-11
### 🚀 Initial Release
- First public release on PyPI.
