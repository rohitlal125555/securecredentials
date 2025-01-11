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

# Generate a unique new key - This needs to be done only once. 
# You need to manually store this key in the environment variables, as the package currently does not automate this step.
unique_key = SecureCredentials.generate_key()
print(unique_key)

# Store/Set the secure field - Encrypt and store the string on disk for later retrieval.
SecureCredentials.set_secure(field='field_name', plaintext='my plaintext string')
print('Field encrypted and stored')

# Get the secured string - Retrieve the encrypted field as needed.
password = SecureCredentials.get_secure(field='field_name')
print(password)
```

## Dependencies

SecureCredentials requires the following Python libraries:

- **cryptography:** For encryption and decryption.
- **python-dotenv:** To manage environment variables.
- **json:** For handling data serialization.
- **pathlib:** For file path operations.
- **logging:** For debugging and logging operations.
- **os:** For system-level operations.

## License

SecureCredentials is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for improvements or feature requests.

## Support

If you encounter issues or have questions, please open an issue in the [GitHub repository](https://github.com/your-repo/securecredentials).

