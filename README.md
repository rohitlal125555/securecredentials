# SecureCredentials

SecureCredentials is a lightweight Python package that encrypts and securely stores key-value pairs on disk, enabling easy and secure retrieval.

## Key Features

- **AES-128 Encryption**: Leverages the industry-standard 128-bit AES algorithm to ensure your data is encrypted and safe.
- **Local Security**: The AES key and encrypted strings are stored locally, ensuring no sensitive data leaves your system.
- **Convenience**: Eliminates the need to store credentials in plain text or repeatedly type them into the console.

## Installation

To install SecureCredentials, run:

```bash
pip install securecredentials
```

## Usage

Below is a basic usage example:

```python
from securecredentials import SecureCredentials

# Generate & store the unique master key - This needs to be done only once. 
master_key = SecureCredentials.generate_master_key()
SecureCredentials.store_master_key(unique_key=master_key)

# Encrypt and store the key-value pair on the disk for later retrieval.
SecureCredentials.set_secure(field='field_name', plaintext='my plaintext string')

# Retrieve the encrypted field as needed.
my_secure_string = SecureCredentials.get_secure(field='field_name')
print(my_secure_string)
```

## Dependencies

SecureCredentials requires the following Python libraries:

- **cryptography:** For encryption and decryption.
- **python-dotenv:** To manage environment variables.

## License

SecureCredentials is licensed under the Apache License Version 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for improvements or feature requests.

## Support

If you encounter issues or have questions, please open an issue in the [GitHub repository](https://github.com/rohitlal125555/securecredentials/issues).

