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

## Dependencies

SecureCredentials requires the following Python libraries:

- **cryptography:** For encryption and decryption.
- **python-dotenv:** To manage environment variables.

## License

SecureCredentials is licensed under the Apache License Version 2.0. 

### Full Documentation:  
Full documentation and usage examples are available in the
[GitHub repository](https://github.com/rohitlal125555/securecredentials)