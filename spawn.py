import subprocess
import threading


def run_process(cmd):
    print('cmd', cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = proc.communicate()
    print('proc.returncode', proc.returncode)
    print('stdout', stdout)
    print('stderr', stderr)


t1 = threading.Thread(target=run_process, args=('sleep 10; date',))
t2 = threading.Thread(target=run_process, args=('sleep 50; date',))

t1.start()
t2.start()

t1.join()
t2.join()

while True:
    1 + 1