import os
import json
import logging
import textwrap
from typing import Optional, Type
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

from .helper import ANSITerminal
from .utils import KeyHandler
from .schema_version import USER_DB_VERSION
from .exceptions import *


class SecureCredentials:
    _is_loaded = False
    _logger = None
    _master_key = None
    _master_db_path = None
    _user_db_path = None
    _passphrase = None
    _master_file = 'master.db'
    _user_file = 'user.db'

    @classmethod
    def initialize(cls: 'Type[SecureCredentials]', log_level: Optional[int] = logging.INFO,
            log_format: Optional[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
        """
        Initialize the SecureCredentials module by setting up logging, creating directories, and loading the master key.

        :param log_level: logging level (default: logging.INFO)
        :param log_format: logging format (default: '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        :return: None
        """
        cls._configure_logging(log_level, log_format)
        cls._initialize_directories()

    @classmethod
    def _configure_logging(cls: 'Type[SecureCredentials]', log_level: int, log_format: str) -> None:
        """
        Configures the logging settings for the SecureCredentials module.

        :param log_level: logging level
        :param log_format: logging format
        :return: None
        """
        logger = logging.getLogger(cls.__name__)

        if not logger.handlers:  # Prevent adding multiple handlers on repeated setup calls
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(console_handler)

        logger.setLevel(log_level)
        cls._logger = logger

    @classmethod
    def __flush_logs(cls: 'Type[SecureCredentials]') -> None:
        """ Flushes all the log handlers to ensure that all logs are written to the output """
        for handler in cls._logger.handlers:
            handler.flush()

    @classmethod
    def _initialize_directories(cls: 'Type[SecureCredentials]') -> None:
        """ Initializes the directories for storing the master key and user database files """
        if os.name == 'nt':
            cls._logger.debug('Initializing the master and user directory. OS detected: Windows')
            cls._master_db_path = os.path.join(*[os.getenv('APPDATA'), cls.__name__, cls._master_file])
            cls._user_db_path = os.path.join(*[os.getenv('LOCALAPPDATA'), cls.__name__, cls._user_file])
        elif os.name == 'posix':
            cls._logger.debug('Initializing the master and user directory. OS detected: Unix/Linux')
            cls._master_db_path = os.path.join(*[os.path.expanduser('~'), '.config', cls.__name__, cls._master_file])
            cls._user_db_path = os.path.join(*[os.path.expanduser('~'), '.local/share', cls.__name__, cls._user_file])
        else:
            raise UnsupportedOSError(f'Unknown OS type detected. This package is not supported for - "{os.name}" OS.')

        # Create the directories if they do not exist
        os.makedirs(os.path.dirname(cls._master_db_path), exist_ok=True)
        os.makedirs(os.path.dirname(cls._user_db_path), exist_ok=True)

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt the given ciphertext using the provided cipher key.

        :param ciphertext: data to be decrypted
        :param key: decryption key (should be 16, 24 or 32 bytes long)
        :param nonce: decryption nonce (should be 12 bytes long)
        :param associated_data: (optional) associated data used for authentication
        :return: decrypted data (in bytes format)
        """
        aes_gcm = AESGCM(key)
        return aes_gcm.decrypt(nonce, ciphertext, associated_data)

    @staticmethod
    def encrypt(plaintext: bytes, key: bytes, associated_data: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Encrypt the given plaintext using the provided cipher key.

        :param plaintext: data to be encrypted (in bytes format)
        :param key: encryption key (should be 16, 24 or 32 bytes long)
        :param associated_data: (optional) associated data used for authentication
        :return: tuple pair of (encrypted_data, nonce)
        """
        aes_gcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        return aes_gcm.encrypt(nonce=nonce, data=plaintext, associated_data=associated_data), nonce

    @staticmethod
    def generate_master_key() -> bytes:
        """ generate a new 256-bit master key for AES-GCM encryption """
        return os.urandom(32)

    @classmethod
    def set_passphrase(cls: 'Type[SecureCredentials]', passphrase: str) -> None:
        """
        Set the passphrase for the master key. This is used to encrypt the master key before storing it on the disk.

        :param passphrase: passphrase to be set
        :return: None
        """
        cls._logger.debug('Setting passphrase for the master key.')
        cls._passphrase = passphrase
        cls._logger.debug('Passphrase loaded for master key encryption/decryption.')

    @classmethod
    def store_master_key(cls: 'Type[SecureCredentials]', master_key: bytes,
                         user_confirmation: Optional[bool] = True) -> None:
        """
        Store the master key on the disk. This method should be called only once during setup.

        :param master_key: master key to be stored (should be 16, 24 or 32 bytes long)
        :param user_confirmation: flag to skip terminal-based confirmation checks in case of daemon process
        :return: None
        """
        cls.__flush_logs()
        if len(master_key) not in (16, 24, 32):
            raise InvalidKeyLengthError('Invalid AES-GCM key length; must be 16, 24, or 32 bytes. '
                                        'You can generate a unique key using "generate_master_key" method.')

        # flag to skip terminal-based confirmation checks in case of daemon process
        if user_confirmation:
            user_response = input(
                ANSITerminal.decorate(
                    text=textwrap.dedent('''
                            Warning: This action is irreversible and will overwrite any existing master key.
                            (You typically need to do this only once during setup.)
                            Any data encrypted with the previous master key will become unrecoverable.
                            
                            Type "y" to confirm and store the new master key, or anything else to cancel.
                            >> '''),
                    color='yellow',
                    style='bold'
                ))
            if user_response.strip().lower() not in ['y', 'yes']:
                cls._logger.info('Discarding action')
                return

        KeyHandler.store_key(key=master_key, passphrase=cls._passphrase, path=cls._master_db_path)
        cls._master_key = master_key
        cls._logger.info('Master key successfully stored on the disk.')

    @classmethod
    def _load_master_key(cls: 'Type[SecureCredentials]') -> None:
        """ Load the master key from the disk if it exists. Log a warning if it does not """

        if not os.path.exists(cls._master_db_path):
            raise MasterDatabaseNotFoundError('No master key database found in the system. '
                           'You can generate and store a new master key by "generate_master_key" and '
                           '"store_master_key" methods.')
        else:
            cls._master_key = KeyHandler.load_key(passphrase=cls._passphrase, path=cls._master_db_path)
            cls._logger.debug('Loaded the Master key from disk')

    @staticmethod
    def _load_store(path):
        """
        Utility function to load a JSON user database from the disk.
        :param path: path to the user database
        :return: json object of the user database
        """
        with open(path, 'r') as fp:
            return json.load(fp)

    @staticmethod
    def _write_store(path, data):
        """
        Utility function to write a JSON user database to the disk.
        :param path: path to the user database
        :param data: json database object to be written
        :return: None
        """
        tmp = path + '.tmp'
        with open(tmp, 'w') as fp:
            json.dump(data, fp, indent=2)
        os.replace(tmp, path)

    @classmethod
    def get_secure(cls: 'Type[SecureCredentials]', field: str, key: Optional[bytes] = None) -> str:
        """
        Retrieve the secure field from the user database. This method decrypts the ciphertext using the master key.

        :param field: name of the field to be retrieved
        :param key: master key to be used for decryption (optional)
        :return: decrypted plaintext string
        """
        if key is None:
            if cls._master_key is None:
                cls._load_master_key()
            key = cls._master_key

        if not os.path.exists(cls._user_db_path):
            raise UserDatabaseNotFoundError(f'No user database found at: "{cls._user_db_path}". '
                                    f'You need to initialize the user database and store the key-value pair first by '
                                    f'calling the "set_secure" method.')

        data_dict = cls._load_store(cls._user_db_path)
        if field not in data_dict['fields']:
            raise SecureFieldNotFoundError(f'Secure field: "{field}" is not found in the user database. '
                           f'You need to set it first using the "set_secure" method.')

        cipher_data = data_dict['fields'][field]
        cls._logger.debug(f'Secure field: "{field}" found in user db.')

        # Decrypt the ciphertext using the master key
        try:
            plaintext = cls.decrypt(
                ciphertext=base64.b64decode(cipher_data['ciphertext']), key=key,
                nonce=base64.b64decode(cipher_data['nonce']), associated_data=None)
            return plaintext.decode('utf-8')
        except InvalidTag as ite:
            raise FieldDecryptionError(
                'Decryption failed. This usually means the master key has changed or is incorrect.'
            ) from ite

    @classmethod
    def set_secure(cls: 'Type[SecureCredentials]', field: str, plaintext: str, key: Optional[bytes] = None,
                   user_confirmation: Optional[bool]=True) -> None:
        """
        Encrypt and store the plaintext value for the given field in the user database.

        :param field: name of the field to be stored
        :param plaintext: plaintext value to be encrypted and stored
        :param key: master key to be used for encryption (optional)
        :param user_confirmation: flag to skip terminal-based confirmation checks in case of daemon process
        :return: None
        """
        if key is None:
            if cls._master_key is None:
                cls._load_master_key()
            key = cls._master_key

        if os.path.exists(cls._user_db_path):
            data_dict = cls._load_store(cls._user_db_path)
        else:
            data_dict = {'version':USER_DB_VERSION, 'fields': {}}

        if field in data_dict['fields']:
            if user_confirmation:
                cls.__flush_logs()
                user_response = input(
                    ANSITerminal.decorate(
                        text=textwrap.dedent(f'''
                            Warning: The field "{field}" already exists in the user database.
                            Type "y" to overwrite its value, or anything else to cancel.
                            >> '''),
                        color='yellow',
                        style='bold'
                    ))
                if user_response.strip().lower() not in ['y', 'yes']:
                    cls._logger.info('Discarding operation')
                    return
            else:
                cls._logger.info(f'Overwriting existing field: "{field}"')

        ciphertext, nonce = cls.encrypt(plaintext=plaintext.encode('utf-8'), key=key, associated_data=None)
        data_dict['fields'][field] = {}
        data_dict['fields'][field]['ciphertext'] = base64.b64encode(ciphertext).decode('utf-8')
        data_dict['fields'][field]['nonce'] = base64.b64encode(nonce).decode('utf-8')

        cls._write_store(cls._user_db_path, data_dict)
        cls._logger.info(f'Field: "{field}" securely encrypted on disk.')

    @classmethod
    def clear_database(cls, database: str, user_confirmation: Optional[bool] = True) -> None:
        """
        Clear the user or master database based on the provided parameter by removing the respective file on disk.
        Caution: This will delete all stored secure fields.

        :param database:
        :param user_confirmation:
        :return:
        """
        if database.lower().strip() == 'master':
            db_path = cls._master_db_path
        elif database.lower().strip() == 'user':
            db_path = cls._user_db_path
        else:
            cls._logger.warning('Invalid database type. Ignoring operation.')
            return

        if user_confirmation:
            cls.__flush_logs()
            user_response = input(
                ANSITerminal.decorate(
                    text=textwrap.dedent(f'''
                        Warning: This operation will clear the "{database}" database and delete all stored secure fields.
                        Press "y" to confirm and clear the database, or anything else to cancel.
                        >> '''),
                    color='yellow',
                    style='bold'
                ))
            if user_response.strip().lower() not in ['y', 'yes']:
                cls._logger.info('Discarding operation')
                return

        if os.path.exists(db_path):
            os.remove(db_path)
            cls._logger.info('User database cleared successfully.')
        else:
            cls._logger.warning(f'Database: "{database}" does not exist. Nothing to clear.')

    @classmethod
    def help(cls: 'Type[SecureCredentials]') -> None:
        """ Display help information for using the SecureCredentials module """
        cls._logger.info(
            ANSITerminal.decorate(
                text=textwrap.dedent('''
                # How to use the SecureCredentials module?
                
                # import the package
                import securecredentials as sc
                
                # Generate a new master key - Only needs to be done once in lifetime
                master_key = sc.generate_master_key()
                
                # Store the master key on the disk - Only needs to be done once in lifetime
                sc.store_master_key(master_key)
                >> [TIMESTAMP] - SecureCredentials - INFO - Master key successfully stored on the disk.
                
                # Store/Set the secure field - Only needs to be done once per unique field. This encrypts and stores
                # the string on the disk for later retrieval
                sc.set_secure(field='date of birth', plaintext='January 1st 1970')
                >> [TIMESTAMP] - SecureCredentials - INFO - Field: "date of birth" securely encrypted on disk.
                
                # Get the secured string - This is the only function you need to call on regular basis, everytime you 
                # need to retrieve the encrypted fields.
                my_secure_string = sc.get_secure(field='date_of_birth')
                >> [TIMESTAMP] - SecureCredentials - INFO - Secure field: "date of birth" found in user db.'''),
                color='aqua',
                style='bold'
            ))
