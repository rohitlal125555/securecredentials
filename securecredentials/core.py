import json
import logging
import os
import textwrap
from pathlib import Path
from typing import Optional, Type

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv, set_key
from .utils import ANSITerminal


class SecureCredentials:
    _master_keyfile_mapping = 'secure_credentials_key'
    _master_key = None
    _master_db_path = None
    _user_db_path = None
    _logger = None

    @classmethod
    def _initialize(cls: 'Type[SecureCredentials]', log_level: int = logging.INFO,
            log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
        """ Set up the SecureCredentials environment, configure logging, and initialize directories."""
        cls._configure_logging(log_level, log_format)
        cls._initialize_directories_and_load_env()
        cls._check_if_master_key_exists()

    @classmethod
    def _configure_logging(cls: 'Type[SecureCredentials]', log_level: int, log_format: str) -> None:
        """ Configure logging for the SecureCredentials class, with provided log level and format."""
        logger = logging.getLogger(cls.__name__)

        if not logger.handlers:  # Prevent adding multiple handlers on repeated setup calls
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(console_handler)

        logger.setLevel(log_level)
        cls._logger = logger

    @classmethod
    def __flush_logs(cls: 'Type[SecureCredentials]') -> None:
        """ Flushes all logs in the logger handlers."""
        for handler in cls._logger.handlers:
            handler.flush()

    @classmethod
    def _initialize_directories_and_load_env(cls: 'Type[SecureCredentials]') -> None:
        """ Initializes directories for storing keys and loads environment variables."""
        if os.name == 'nt':
            cls._logger.debug('Initializing the master and user directory. OS detected: Windows')
            master_db_dir = os.path.join(*[os.getenv('APPDATA'), cls.__name__])
            user_db_dir = os.path.join(*[os.getenv('LOCALAPPDATA'), cls.__name__])
        elif os.name == 'posix':
            cls._logger.debug('Initializing the master and user directory. OS detected: Unix/Linux')
            master_db_dir = os.path.join(*[os.path.expanduser('~'), '.config', cls.__name__])
            user_db_dir = os.path.join(*[os.path.expanduser('~'), '.local/share', cls.__name__])
        else:
            raise OSError(f'Unknown OS type detected. This package is not supported for - "{os.name}" OS.')

        Path(master_db_dir).mkdir(parents=True, exist_ok=True)
        Path(user_db_dir).mkdir(parents=True, exist_ok=True)

        master_db = os.path.join(master_db_dir, 'master_key.env')
        user_db = os.path.join(user_db_dir, 'secure_credentials.db')

        load_dotenv(dotenv_path=master_db)
        cls._logger.debug('Environment variables refreshed.')

        cls._master_db_path = master_db
        cls._user_db_path = user_db

    @classmethod
    def _check_if_master_key_exists(cls: 'Type[SecureCredentials]') -> None:
        """ Check if the master key exists in the environment. Logs a warning if not."""
        env_key = os.getenv(cls._master_keyfile_mapping)
        if env_key is None:
            cls._logger.warning(textwrap.dedent(f'''
            No secret key found in the environment.  
            You can generate and store a new master key by "generate_master_key" and "store_master_key" methods.'''))
        else:
            cls._master_key = env_key
            cls._logger.debug('Successfully read the Master key from disk.')

    @classmethod
    def store_master_key(cls: 'Type[SecureCredentials]', unique_key: str, user_confirmation: bool = True) -> None:
        """ Store the master key securely after confirming with the user."""
        cls.__flush_logs()
        if len(unique_key) != 44:
            raise KeyError('Fernet key must be 32 base64 characters long. You can generate a unique '
                           'key using "generate_master_key" method.')

        if user_confirmation:
            user_response = input(
                ANSITerminal.decorate(
                    text=textwrap.dedent('''
                            Warning: This operation is irreversible and will overwrite any existing master key.
                            (Typically you only need to run it once during setup.)
                            Data encrypted with the old master key (if any) will no longer decrypt.
                            
                            Type "y" to confirm and store the new master key, or anything else to cancel.
                            >> '''),
                    color='yellow',
                    style='bold'
                ))
            if user_response.strip().lower() not in ['y', 'yes']:
                cls._logger.info('Discarding operation')
                return

        set_key(cls._master_db_path, cls._master_keyfile_mapping, unique_key)
        cls._logger.info('Master key successfully stored on the disk.')
        cls._master_key = unique_key

    @staticmethod
    def generate_master_key() -> str:
        """ Generate a new Fernet master key and returns it as a string."""
        key = Fernet.generate_key()
        return key.decode('utf-8')

    @staticmethod
    def decrypt(ciphertext: bytes, key: str) -> str:
        """ Decrypt the given ciphertext using the provided cipher key."""
        f = Fernet(key.encode('utf-8'))
        return f.decrypt(ciphertext).decode('utf-8')

    @staticmethod
    def encrypt(plaintext: str, key: str) -> bytes:
        """ Encrypts the given plaintext using the provided cipher key."""
        f = Fernet(key.encode('utf-8'))
        return f.encrypt(plaintext.encode('utf-8'))

    @classmethod
    def get_secure(cls: 'Type[SecureCredentials]', field: str, key: Optional[str] = None) -> str:
        """ Retrieves and decrypts a secure field from the user database."""
        if key is None:
            if cls._master_key is None:
                raise KeyError('Cryptography key is neither present in the environment variables, '
                               'nor is passed as function parameter.')
            else:
                key = cls._master_key

        if not os.path.exists(cls._user_db_path):
            raise FileNotFoundError(f'No user database found at: "{cls._user_db_path}". '
                                    f'You need to initialize the user database and store the key-value pair by calling '
                                    f'the "set_secure" method.')

        with open(cls._user_db_path, 'r') as fp:
            data_dict_serialized = fp.read()
        data_dict = json.loads(data_dict_serialized)

        if field not in data_dict:
            raise KeyError(f'Secure field: "{field}" is not found in the user database. '
                           f'You need to set it first using the "set_secure" method.')

        ciphertext = data_dict[field]

        try:
            f = Fernet(key.encode('utf-8'))
            plaintext = f.decrypt(ciphertext.encode('utf-8'))
        except InvalidToken as e:
            raise ValueError(
                "Decryption failed. This error commonly occurs when the data was encrypted using a different master key."
            ) from e

        cls._logger.debug(f'Secure field: "{field}" found in user db.')
        return plaintext.decode('utf-8')

    @classmethod
    def set_secure(cls: 'Type[SecureCredentials]', field: str, plaintext: str, key: Optional[str] = None, user_confirmation=True) -> None:
        """ Encrypts and stores a secure field in the user database."""
        if key is None:
            if cls._master_key is None:
                raise KeyError('Cryptography key is neither present in the environment variables, '
                               'nor is passed as function parameter.')
            else:
                key = cls._master_key

        if os.path.exists(cls._user_db_path):
            with open(cls._user_db_path, 'r') as fp:
                data_dict_serialized = fp.read()
            data_dict = json.loads(data_dict_serialized)
        else:
            data_dict = {}

        if field in data_dict:
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

        f = Fernet(key.encode('utf-8'))
        ciphertext = f.encrypt(plaintext.encode('utf-8'))
        data_dict[field] = ciphertext.decode('utf-8')
        data_dict_serialized = json.dumps(data_dict)

        with open(cls._user_db_path, 'w') as fp:
            fp.write(data_dict_serialized)
        cls._logger.info(f'Field: "{field}" securely encrypted on disk.')

    # @staticmethod
    @classmethod
    def help(cls: 'Type[SecureCredentials]') -> None:
        """ Logs helpful instructions on how to use the SecureCredentials module."""
        cls._logger.info(textwrap.dedent('''
            # How to use the SecureCredentials module?
            
            # import the package
            import securecredentials as sc
            
            # Generate a new master key - Only needs to be done once in lifetime
            master_key = sc.generate_master_key()
            
            # Store the master key on the disk - Only needs to be done once in lifetime
            sc.store_master_key(unique_key=master_key)
            >> [TIMESTAMP] - SecureCredentials - INFO - Master key successfully stored on the disk.
            
            # Store/Set the secure field - Only needs to be done once per unique field. This encrypts and stores
            # the string on the disk for later retrieval
            sc.set_secure(field='date of birth', plaintext='January 1st 1970')
            >> [TIMESTAMP] - SecureCredentials - INFO - Field: "date of birth" securely encrypted on disk.
            
            # Get the secured string - This is the only function you need to call on regular basis, everytime you 
            # need to retrieve the encrypted fields.
            my_secure_string = sc.get_secure(field='date_of_birth')
            >> [TIMESTAMP] - SecureCredentials - INFO - Secure field: "date of birth" found in user db.
            
            '''))
