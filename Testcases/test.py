import os
import subprocess


script_dir = os.path.dirname(__file__)
package_dir = os.path.abspath(os.path.join(script_dir, '..'))
pos_path = os.path.abspath(os.path.join(script_dir, 'pos'))
neg_path = os.path.abspath(os.path.join(script_dir, 'neg'))
pos_files = os.listdir(pos_path)
neg_files = os.listdir(neg_path)

check_output = False
failed_pos = []
failed_neg = []


print("Testing", pos_path)
for file in pos_files:
    f_file = os.path.abspath(os.path.join(pos_path, file))
    cmd = f"python -m compiler -compile {f_file}".split(' ')
    print(file, end=': ')
    sub = subprocess.run(cmd, cwd=package_dir, capture_output=True, check=check_output)
    if sub.returncode == 0:
        print('success')
    else:
        failed_pos.append(file)
        print(sub.returncode)
        print(sub.stderr.decode())


print("Testing", neg_path)
for file in neg_files:
    f_file = os.path.abspath(os.path.join(neg_path, file))
    cmd = f"python -m compiler -compile {f_file}".split(' ')
    print(file, end=': ')
    sub = subprocess.run(cmd, cwd=package_dir, capture_output=True, check=check_output)
    if sub.returncode != 0:
        print('success')
    else:
        failed_neg.append(file)
        print('FAILED')

print()
if failed_pos:
    print('Failed files in pos:')
    print(failed_pos)
if failed_neg:
    print('Failed files in neg:')
    print(failed_neg)
