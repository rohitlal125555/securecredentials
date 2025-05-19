# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [2.0] - 2025-05-20

This upgrade has major design changes leading to significant security improvements. This update **is not** 
backward compatible. 

For migration from 1.x to 2.x, you'll need to recreate the master key and re-encrypt all your secrets. 
This is straightforward, but please raise an issue on GitHub repo if you encounter any problems.

### Added
- Upgraded to AES-GCM 256-bit encryption 
- Implemented dual encryption scheme to encrypt master keys with deterministic key derived (PBKDF2HMAC) 
from user environment.
- Standardized version control of user and master database schemas. 
  
### Changed
- Removed Fernet 128-bit encryption.
- Master key is no longer stored in plaintext.

---

## [1.3.3] - 2025-05-01
### Added
- Added support for ANSI escape codes in the windows command prompt.

---

## [1.3.2] - 2025-04-22
### Added
- Bug-fixes in the help function.

---

## [1.3.1] - 2025-04-19

Major update with new dynamic module interface. Backward compatibility is maintained.

### Added
- Implemented dynamic module interface for easier imports
- Streamlined internal libraries

---

## [1.1] - 2025-01-11
### Added
- Initial PyPI release.
