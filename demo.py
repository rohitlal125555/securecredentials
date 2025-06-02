import securecredentials as sc

# help function
# sc.help()

# For using the module in PASSPHRASE mode (and not default SYSTEM mode)
# sc.set_passphrase('rohit')

# generate a new master key
# master_key = sc.generate_master_key()

# store the master key on the disk
# sc.store_master_key(master_key=master_key)

# encrypt and store the key-value pair
# sc.set_secure('date of birth', 'January 1st 1970')

# retrieve the stored value for key
# secure_field = sc.get_secure('date of birth')
# print(secure_field)

# clear the user/master database
# sc.clear_database('MASTER')