print('Examining the hanging C function...')

from crystal_torture import tort

print('Testing ctypes function access...')
tort.tort_mod.allocate_nodes(2, 1)

print('Testing raw ctypes call...')
try:
    # Access the global _tort_lib variable directly
    from crystal_torture.tort import _tort_lib
    print('Library accessed successfully')
    
    # Test available functions
    print('Available functions:')
    for name in ['allocate_nodes', 'get_uc_tort_size', 'get_uc_tort']:
        if hasattr(_tort_lib, name):
            print('  ✓ ' + name)
        else:
            print('  ✗ ' + name + ' missing')
            
    # Test the problematic function with timeout
    print('Testing get_uc_tort_size with 1 second timeout...')
    import signal
    signal.alarm(1)
    try:
        size = _tort_lib.get_uc_tort_size()
        print('Success: size = ' + str(size))
    except:
        print('Raw function call hangs too')
    finally:
        signal.alarm(0)
        
except Exception as e:
    print('Error: ' + str(e))
finally:
    tort.tort_mod.tear_down()
