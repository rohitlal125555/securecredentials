import json
import logging
import os
import textwrap
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv, set_key


class SecureCredentials:
    MASTER_KEYFILE_MAPPING = 'secure_credentials_key'
    MASTER_KEY = None
    MASTER_DB = None
    USER_DB = None
    logger = None

    @classmethod
    def setup(cls, log_level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        cls._configure_logging(log_level, log_format)
        cls._initialize_directories_and_load_env()
        cls._check_if_master_key_exists()

    @classmethod
    def _configure_logging(cls, log_level, log_format):
        """Class method to configure logging for the SecureCredentials class."""
        logger = logging.getLogger(cls.__name__)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)
        logger.setLevel(log_level)
        cls.logger = logger

    @classmethod
    def __flush_logs(cls):
        for handler in cls.logger.handlers:
            handler.flush()

    @classmethod
    def _initialize_directories_and_load_env(cls):
        if os.name == 'nt':
            cls.logger.debug('Initializing the master and user directory. OS detected: Windows')
            master_db_dir = os.path.join(*[os.getenv('APPDATA'), cls.__name__])
            user_db_dir = os.path.join(*[os.getenv('LOCALAPPDATA'), cls.__name__])
        elif os.name == 'posix':
            cls.logger.debug('Initializing the master and user directory. OS detected: Unix/Linux')
            master_db_dir = os.path.join(*[os.path.expanduser('~'), '.config', cls.__name__])
            user_db_dir = os.path.join(*[os.path.expanduser('~'), '.local/share', cls.__name__])
        else:
            raise OSError(f'Unknown OS type detected. This package is not supported for - "{os.name}" OS.')

        Path(master_db_dir).mkdir(parents=True, exist_ok=True)
        Path(user_db_dir).mkdir(parents=True, exist_ok=True)

        master_db = os.path.join(master_db_dir, 'master_key.env')
        user_db = os.path.join(user_db_dir, 'secure_credentials.db')

        load_dotenv(dotenv_path=master_db)
        cls.logger.debug('Environment variables refreshed.')

        cls.MASTER_DB = master_db
        cls.USER_DB = user_db

    @classmethod
    def _check_if_master_key_exists(cls):
        env_key = os.getenv(cls.MASTER_KEYFILE_MAPPING)
        if env_key is None:
            cls.logger.warning(textwrap.dedent(f'''
            No secret key found in the environment.  
            You can generate and store a new master key by "generate_master_key" and "store_master_key" methods.'''))
        else:
            cls.MASTER_KEY = env_key
            cls.logger.debug('Successfully read the Master key from disk.')

    @classmethod
    def store_master_key(cls, unique_key):
        cls.__flush_logs()
        if len(unique_key) != 44:
            raise KeyError('Fernet key must be 32 base64 characters long. You can generate a unique '
                           'key using "generate_master_key" method.')

        user_response = input(textwrap.dedent('''
            !!! WARNING !!! 
            This operation is irreversible. It needs to be executed only once during package setup.
            and will overwrite any previous master keys (if it exists).
            If there are any key-value pairs encrypted using old master key, they will cease to work.
            Type "Y" to confirm and store the new master key, or type anything else to discard.
            >> '''))
        if str(user_response).lower() in ['y', 'yes']:
            set_key(cls.MASTER_DB, cls.MASTER_KEYFILE_MAPPING, unique_key)
            cls.logger.info('Master key successfully stored on the disk.')
            cls.MASTER_KEY = unique_key
        else:
            cls.logger.info('Discarding operation')

    @staticmethod
    def generate_master_key():
        key = Fernet.generate_key()
        return key.decode('utf-8')

    @staticmethod
    def decrypt(ciphertext, key):
        f = Fernet(key.encode('utf-8'))
        return f.decrypt(ciphertext)

    @staticmethod
    def encrypt(plaintext, key):
        f = Fernet(key.encode('utf-8'))
        return f.encrypt(plaintext)

    @classmethod
    def get_secure(cls, field, key=None):
        if key is None:
            if cls.MASTER_KEY is None:
                raise KeyError('Cryptography key is neither present in the environment variables, '
                               'nor is passed as function parameter.')
            else:
                key = cls.MASTER_KEY

        if not os.path.exists(cls.USER_DB):
            raise FileNotFoundError(f'No user database found at: "{cls.USER_DB}". '
                                    f'You need to initialize the user database and store the key-value pair by calling '
                                    f'the "set_secure" method.')

        with open(cls.USER_DB, 'r') as fp:
            data_dict_serialized = fp.read()
        data_dict = json.loads(data_dict_serialized)

        if field not in data_dict:
            raise KeyError(f'Secure field: "{field}" is not found in the user database. '
                           f'You need to set it first using the "set_secure" method.')

        ciphertext = data_dict[field]
        f = Fernet(key.encode('utf-8'))
        plaintext = f.decrypt(ciphertext.encode('utf-8'))
        cls.logger.info(f'Secure field: "{field}" found in user db.')
        return plaintext.decode('utf-8')

    @classmethod
    def set_secure(cls, field, plaintext, key=None):
        if key is None:
            if cls.MASTER_KEY is None:
                raise KeyError('Cryptography key is neither present in the environment variables, '
                               'nor is passed as function parameter.')
            else:
                key = cls.MASTER_KEY

        if os.path.exists(cls.USER_DB):
            with open(cls.USER_DB, 'r') as fp:
                data_dict_serialized = fp.read()
            data_dict = json.loads(data_dict_serialized)
        else:
            data_dict = {}

        if field in data_dict:
            cls.__flush_logs()
            user_response = input(textwrap.dedent(f'''
                !!! WARNING !!! 
                The field: "{field}" already exists in the user db.
                Do you want to override the existing value?
                Type "Y" to confirm and store the new master key, or type anything else to discard.
                >> '''))
            if str(user_response).lower() not in ['y', 'yes']:
                cls.logger.info('Discarding operation')
                return

        f = Fernet(key.encode('utf-8'))
        ciphertext = f.encrypt(plaintext.encode('utf-8'))
        data_dict[field] = ciphertext.decode('utf-8')
        data_dict_serialized = json.dumps(data_dict)

        with open(cls.USER_DB, 'w') as fp:
            fp.write(data_dict_serialized)
        cls.logger.info(f'Field: "{field}" securely encrypted on disk.')

    # @staticmethod
    @classmethod
    def help(cls):
        cls.logger.info(textwrap.dedent('''
            # How to use the SecureCredentials module?
            
            # import the package
            from securecredentials import SecureCredentials
            
            # generate a new key - This needs to be done only once in lifetime. This key needs to be stored
            # in the environment variables.
            unique_key = SecureCredentials.generate_key()
            print(unique_key)
            
            # Store/Set the secure field - Only needs to be done once per unique field. This encrypts and stores
            # the string on the disk for later retrieval
            
            SecureCredentials.set_secure(field='field_name', plaintext='my plaintext string')
            print('Field encrypted and stored')
            
            # Get the secured string - This is the only function you need to call on regular basis, everytime you 
            # need to retrieve the encrypted fields.
            
            password = SecureCredentials.get_secure(field='field_name')
            print(password)'''))


SecureCredentials.setup(log_level=logging.INFO)
