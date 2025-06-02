
class DecryptionError(Exception):
    """Raised when decryption fails due to incorrect key or corrupted ciphertext."""
    pass

class MasterKeyDecryptionError(DecryptionError):
    """Raised when decryption of the master key fails."""
    pass

class FieldDecryptionError(DecryptionError):
    """Raised when decryption of an individual field fails."""
    pass

class PassphraseRequiredError(Exception):
    """Raised when a passphrase is required but not provided."""
    pass

class PassphraseNotAllowedError(Exception):
    """Raised when a passphrase is provided but not expected."""
    pass

class UserDatabaseNotFoundError(FileNotFoundError):
    """Raised when the user database file is missing."""
    pass

class MasterDatabaseNotFoundError(FileNotFoundError):
    """Raised when the master key database file is not found."""
    pass

class UnsupportedOSError(OSError):
    """Raised when the current OS is not supported by SecureCredentials."""
    pass

class SecureFieldNotFoundError(KeyError):
    """Raised when a requested secure field is not found in the user database."""
    pass

class InvalidKeyLengthError(ValueError):
    """Raised when the AES-GCM key length is invalid (must be 16, 24, or 32 bytes)."""
    pass

class DatabaseError(Exception):
    """Base class for database-related errors."""
    pass

class SchemaVersionError(DatabaseError):
    """Raised for schema version mismatches."""
    pass

