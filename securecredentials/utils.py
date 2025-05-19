import os
import platform
import getpass
from typing import Optional, Type
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .schema_version import MASTER_DB_VERSION

class KeyHandler:
    """
    An internal-use only class to handle the master key storage.
    """

    _salt_size = 16  # 128-bit random salt for KDF
    _nonce_size = 12  # 96-bit nonce for GCM
    _vheader_size = len(bytes([MASTER_DB_VERSION]))  # 1 byte for schema version

    @classmethod
    def _get_deterministic_kek(cls: 'Type[KeyHandler]', salt: bytes) -> bytes:
        """
        Generate a 256 bit deterministic Key-Encryption-Key (KEK) based on system/environment identifiers and given salt

        :param salt: random salt for KDF
        :return: deterministic KEK (bytes)
        """

        kek_seed = ''.join([
            platform.node(),  # hostname
            platform.system(),  # OS name
            platform.machine(),  # machine type
            platform.processor(),  # processor name
            getpass.getuser(),  # username
        ]).encode()

        # Derive 32-byte key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
            backend=default_backend(),
        )
        return kdf.derive(key_material=kek_seed)

    @classmethod
    def store_key(cls: 'Type[KeyHandler]', key: bytes, path: str) -> None:
        """
        encrypt & store the master key using 256 bit deterministic KEK

        :param key: key to store
        :param path: full path of the file to store the key
        :return: None
        """

        schema_version = bytes([MASTER_DB_VERSION])
        salt = os.urandom(cls._salt_size)
        aes_key = cls._get_deterministic_kek(salt)

        aes_gcm = AESGCM(aes_key)
        nonce = os.urandom(cls._nonce_size)
        encrypted_master_key = aes_gcm.encrypt(nonce=nonce, data=key, associated_data=None)

        with open(path, 'wb') as f:
            f.write(schema_version + salt + nonce + encrypted_master_key)

    @classmethod
    def load_key(cls: 'Type[KeyHandler]', path: str) -> bytes:
        """
        decrypt & load the master key using 256 bit deterministic KEK
        :param path: full path of the file to load the key
        :return: master key (bytes)
        """

        with open(path, 'rb') as f:
            blob = f.read()

        # size and order of each header component
        header_struct = [cls._vheader_size, cls._salt_size, cls._nonce_size]

        # calculate end offsets of each header component
        header_indexes = [sum(header_struct[:i+1]) for i in range(len(header_struct))]

        version = blob[:header_indexes[0]]
        # Version functionality can be used in the future to help in migration between different versions of the schema.
        # if version != bytes([MASTER_DB_VERSION]):
        #     raise ValueError(f"Unsupported master schema version: {version}")

        aes_key = cls._get_deterministic_kek(salt=blob[header_indexes[0]:header_indexes[1]])
        aes_gcm = AESGCM(aes_key)
        master_key = aes_gcm.decrypt(
            nonce=blob[header_indexes[1]:header_indexes[2]],
            data=blob[header_indexes[2]:],
            associated_data=None)

        return master_key
