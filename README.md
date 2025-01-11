# SecureCredentials

SecureCredentials is a lightweight Python package designed to securely store key-value pairs, such as passwords 
or other sensitive information, on disk. By leveraging strong encryption, the package ensures that your sensitive 
data remains safe while providing convenient access for everyday use.

## Why SecureCredentials Was Created
This package was created to address two common challenges faced by developers:

1. **Avoid storing sensitive credentials in plaintext:** It is unsafe for developers to store credentials such as 
database passwords, Active Directory passwords, and API keys in plaintext within their scripts or configuration files.
2. **Eliminate the need to repeatedly enter passwords:** Developers often have to enter their credentials every 
time they run a script, which can be cumbersome and error-prone. SecureCredentials allows for automatic retrieval 
of encrypted credentials, eliminating the need to type them each time.

## Key Features

- **AES-128 Encryption**: Leverages the industry-standard 128-bit AES algorithm to ensure your data is encrypted 
and safe.
- **Local Security**: The AES key and encrypted data is stored locally, ensuring that no sensitive data leaves 
your system.
- **Convenience**: The package streamlines the process by enabling automated, secure access to credentials, so 
you do not have to store them in plaintext or type them in each time you run your scripts.

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

