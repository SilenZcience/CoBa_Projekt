import os
import subprocess
import sys



script_dir = os.path.dirname(__file__)
package_dir = os.path.abspath(os.path.join(script_dir, '..'))
pos_path = os.path.abspath(os.path.join(script_dir, 'pos'))
neg_path = os.path.abspath(os.path.join(script_dir, 'neg'))
pos_files = os.listdir(pos_path)
neg_files = os.listdir(neg_path)

check_output = False
failed_pos = []
failed_neg = []

CMD_compile = 'python -m compiler -compile'.split(' ')
CMD_liveness = 'python -m compiler -liveness'.split(' ')
CONST_SUCCESS = 'success'
CONST_FAILED = 'FAILED'
l_msg = ''
l_error_code = 0

ONLY_ID = -1
if len(sys.argv) > 1:
    ONLY_ID = int(sys.argv[1])

if ONLY_ID > -1:
    f_file = os.path.abspath(os.path.join(
        pos_path, [file for file in pos_files if file[-3:] == '.jl'][ONLY_ID]))
    sub = subprocess.run(CMD_liveness + [f_file, '-debug'],
                         cwd=package_dir, capture_output=True, check=check_output)
    print(sub.stdout.decode())
    print(sub.stderr.decode())
    if sub.returncode > 0:
        sys.exit(sub.returncode)
    sub = subprocess.run(CMD_compile + [f_file, '-debug'],
                         cwd=package_dir, capture_output=True, check=check_output)
    print(sub.stdout.decode())
    print(sub.stderr.decode())
    if sub.returncode > 0:
        sys.exit(sub.returncode)
    sub = subprocess.run('java -jar ./jasmin.jar'.split(' ') + [f_file[:-1]],
                         cwd=package_dir, capture_output=True, check=check_output)
    print(sub.stdout.decode())
    print(sub.stderr.decode())
    if sub.returncode > 0:
        sys.exit(sub.returncode)
    sub = subprocess.run('java -cp .'.split(' ') + [f_file[f_file.rfind('\\')+1:-3]],
                         cwd=package_dir, capture_output=True, check=check_output)
    print(sub.stdout.decode())
    print(sub.stderr.decode())
    if sub.returncode > 0:
        sys.exit(sub.returncode)
    sys.exit(0)

print('Testing', pos_path)
for file in pos_files:
    f_file = os.path.abspath(os.path.join(pos_path, file))
    if f_file[-3:] != '.jl':
        continue
    sub = subprocess.run(CMD_compile + [f_file], cwd=package_dir, capture_output=True, check=check_output)
    if l_error_code == 0:
        print('\b' * len(l_msg), end='')
        print(' ' * len(l_msg), end='')
        print('\b' * len(l_msg), end='')
    l_msg = f"{file}: "
    l_error_code = sub.returncode
    if l_error_code == 0:
        l_msg += CONST_SUCCESS
        print(l_msg, end='')
    else:
        failed_pos.append(file)
        l_msg += f"{l_error_code}\n{sub.stderr.decode()}"
        print(l_msg)
    print('', end='', flush=True)
if l_error_code == 0:
    print('\b' * len(l_msg), end='')
    print(' ' * len(l_msg), end='')
    print('\b' * len(l_msg), end='')

print('\nTesting', neg_path)
for file in neg_files:
    f_file = os.path.abspath(os.path.join(neg_path, file))
    if f_file[-3:] != '.jl':
        continue
    sub = subprocess.run(CMD_compile + [f_file], cwd=package_dir, capture_output=True, check=check_output)
    if l_error_code != 0:
        print('\b' * len(l_msg), end='')
        print(' ' * len(l_msg), end='')
        print('\b' * len(l_msg), end='')
    l_msg = f"{file}: "
    l_error_code = sub.returncode
    if l_error_code != 0:
        l_msg += CONST_SUCCESS
        print(l_msg, end='')
    else:
        failed_neg.append(file)
        l_msg += f"{CONST_FAILED}"
        print(l_msg)
    print('', end='', flush=True)
if l_error_code != 0:
    print('\b' * len(l_msg), end='')
    print(' ' * len(l_msg), end='')
    print('\b' * len(l_msg), end='')


print('\n' + '-' * (len(pos_path)+8))
if failed_pos:
    print('Failed files in pos:')
    print(failed_pos)
if failed_neg:
    print('Failed files in neg:')
    print(failed_neg)
if not failed_pos and not failed_neg:
    print('All tests successfull.')
