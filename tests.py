# Creating this script for testing the securecredentials module
# This is not a fully automated test script.

def test_1():
    import securecredentials as sc
    sc.help()

def test_2():
    import securecredentials as sc
    secure_field = sc.get_secure('date of birth')
    print(secure_field)

def test_3():
    import securecredentials as sc
    sc.set_secure('date of birth', 'January 1st 1970')

def test_4():
    import securecredentials as sc
    master_key = sc.generate_master_key()
    sc.store_master_key(master_key=master_key)

def test_5():
    test_2()

def test_6():
    test_3()

def test_7():
    test_2()

def test_8():
    test_4()

def test_9():
    test_2()

def test_10():
    test_3()

def test_11():
    test_2()

if __name__ == '__main__':
    # test_1()
    # test_2()
    # test_3()
    # test_4()
    # test_5()
    # test_6()
    # test_7()
    # test_8()
    # test_9()
    # test_10()
    test_11()