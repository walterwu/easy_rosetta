import subprocess
from os import path
from random import randint

DEFAULT_CONFIG_PATH = path.join(path.dirname(__file__), "data/configs/default_config")
SESSION_CONFIG_PATH = path.join(path.dirname(__file__), "data/configs/session_config")

def run_cmd(command, ignore_error=False, display_stdout=True, cwd=None):
    proc = subprocess.Popen(command, shell=True, cwd=cwd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    exitcode = proc.returncode
    out, err = proc.communicate()
    if display_stdout:
        output = out.decode()
        if output:
            print(output)
    if not ignore_error and exitcode:
        print("Command: {} was expected to succeed, returned {}".format(command, exitcode))
        print("BEGIN STDERROR")
        print("*" * 20)
        print(err.decode())
        print("*" * 20)
        print("END STDERROR")
        raise subprocess.SubprocessError
    
def pythonify_path(path):
    return path.replace("\\ ", " ")

def shellify_path(path):
    return path.replace(" ", "\\ ")

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def file_replace(pattern, data, file):
    new_lines = []
    with open(file, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            line = line.replace(pattern, data)
            new_lines.append(line)
    with open(file, 'w') as fp:
        fp.writelines(new_lines)

def copy_to_config(file):
    for key, value in parse_configfile(file).items():
        write_config(key, value)

def read_config(file):
    ret_dict = {}
    with open(file) as fp:
        line = fp.readline()
        while line:
            tokens = line.replace('\n', '').split(':')
            ret_dict[tokens[0]] = tokens[1]
            line = fp.readline()
    return ret_dict

def search_config(file):
    config = read_config(file)
    if key in config:
        return config[key]
    return None

def write_config(key, value, file):
    if ':' in str(key) or ':' in str(value):
        raise ValueError("Illegal character \":\" found in key or value.")
    config = read_config(file)
    config[key] = value
    with open(file, 'w') as fp:
        for key, value in config.items():
            fp.write(str(key) + ":" + str(value) + '\n')


