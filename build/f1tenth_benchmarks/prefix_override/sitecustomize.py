import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ecd508/f1tenth_ws_4/install/f1tenth_benchmarks'
