import os
import json
import platform
import getpass
import base64
from typing import Type

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from .schema_version import MASTER_DB_VERSION
from .exceptions import *


class KeyHandler:
    """
    An internal-use only class to handle the master key storage.
    """
    _salt_size = 16  # 128-bit random salt for KDF
    _nonce_size = 12  # 96-bit nonce for GCM

    @classmethod
    def _get_deterministic_kek(cls: 'Type[KeyHandler]', salt: bytes) -> bytes:
        """
        Generate a 256 bit deterministic Key-Encryption-Key (KEK) based on system/environment identifiers and salt

        :param salt: random salt for KDF
        :return: deterministic KEK (bytes)
        """

        kek_seed = ''.join([
            platform.node().strip().lower(), # hostname
            platform.system().strip().lower(), # OS name
            platform.machine().strip().lower(), # machine type
            platform.processor().strip().lower(), # processor name
            getpass.getuser().strip().lower(), # username
        ]).encode()

        # Derive 32-byte key using Scrypt
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2 ** 16,  # CPU/memory cost
            r=8,  # Block size
            p=1,  # Parallelization
        )
        return kdf.derive(key_material=kek_seed)

    @classmethod
    def _get_kek_from_passphrase(cls: 'Type[KeyHandler]', passphrase: str, salt: bytes) -> bytes:
        """
        Generate a 256 bit Key-Encryption-Key (KEK) based on the given passphrase and salt

        :param passphrase: passphrase to derive KEK
        :param salt: random salt for KDF
        :return: KEK (bytes)
        """

        if salt is None:
            salt = os.urandom(cls._salt_size)

        # Derive 32-byte key using KDF
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2 ** 16,  # CPU/memory cost
            r=8,  # Block size
            p=1,  # Parallelization
        )
        return kdf.derive(key_material=passphrase.encode('utf-8'))

    @classmethod
    def store_key(cls: 'Type[KeyHandler]', key: bytes, passphrase: str, path: str) -> None:
        """
        encrypt & store the master key using 256 bit deterministic KEK

        :param passphrase: passphrase to derive KEK
        :param key: key to store
        :param path: full path of the file to store the key
        :return: None
        """
        salt = os.urandom(cls._salt_size)
        if passphrase is None:
            mode = 'system'
            aes_key = cls._get_deterministic_kek(salt)
        else:
            mode = 'passphrase'
            aes_key = cls._get_kek_from_passphrase(passphrase, salt)

        aes_gcm = AESGCM(aes_key)
        nonce = os.urandom(cls._nonce_size)
        encrypted_master_key = aes_gcm.encrypt(nonce=nonce, data=key, associated_data=None)

        # Write the encrypted key to a file with metadata
        tmp = path + '.tmp'
        with open(tmp, 'w') as fp:
            json.dump({
                'mode': mode,
                'schema_version': str(MASTER_DB_VERSION),
                'salt': base64.b64encode(salt).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'data': base64.b64encode(encrypted_master_key).decode('utf-8'),
            }, fp, indent=2)
        os.replace(tmp, path)

    @classmethod
    def load_key(cls: 'Type[KeyHandler]', passphrase: str, path: str) -> bytes:
        """
        decrypt & load the master key using 256 bit deterministic KEK
        :param passphrase: passphrase to derive KEK
        :param path: full path of the file to load the key
        :return: master key (bytes)
        """

        with open(path, 'r') as fp:
            json_data = json.load(fp)

        version = json_data['schema_version']
        # Version functionality can be used in the future to help in migration between different versions of the schema.
        # if version != bytes([MASTER_DB_VERSION]):
        #     raise SchemaVersionError(f"Unsupported master schema version: {version}")

        if json_data['mode'] == 'passphrase':
            if not passphrase:
                raise PassphraseRequiredError(
                    'Passphrase is required when the master key is stored in PASSPHRASE mode. '
                    'Please load the passphrase first using the "set_passphrase" method.')
            else:
                aes_key = cls._get_kek_from_passphrase(passphrase, base64.b64decode(json_data['salt']))
        else:
            if passphrase:
                raise PassphraseNotAllowedError(
                    'Passphrase should not be provided when master key is stored in SYSTEM mode. '
                    'Do not use "set_passphrase" method when master key is stored in SYSTEM mode.')
            else:
                aes_key = cls._get_deterministic_kek(salt=base64.b64decode(json_data['salt']))

        aes_gcm = AESGCM(aes_key)

        try:
            master_key = aes_gcm.decrypt(
                nonce=base64.b64decode(json_data['nonce']),
                data=base64.b64decode(json_data['data']),
                associated_data=None)
            return master_key

        except InvalidTag as ite:
            if json_data['mode'] == 'passphrase':
                raise MasterKeyDecryptionError('Decryption failed: Incorrect passphrase. '
                                 'Double check and set the correct passphrase using the "set_passphrase" method.'
                                 ) from ite
            else:
                raise MasterKeyDecryptionError(
                    'Decryption failed: System identity has changed.'
                    'To fix this, reset the master key using the "generate_master_key" and "store_master_key" methods. '
                    'Note: Previously encrypted fields cannot be recovered after resetting the master key.'
                ) from ite