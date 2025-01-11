from securecredentials import SecureCredentials

# help function
# SecureCredentials.help()

# generate a new master key
master_key = SecureCredentials.generate_master_key()

# store the master key on the disk
SecureCredentials.store_master_key(unique_key=master_key)

# encrypt and store the key-value pair
SecureCredentials.set_secure('password', 'rohit-pass')

# retrieve the stored value for key
secure_field = SecureCredentials.get_secure('password')
