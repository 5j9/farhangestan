#!/usr/bin/env python3
from subprocess import check_call, check_output
from pathlib import Path
from os import chdir

home = Path.home()
try:
    (home / 'uwsgi.log').unlink()
except FileNotFoundError:
    pass
chdir(b'/data/project/farhangestan/www/python/src')
check_call(b'git reset --hard && git pull', shell=True)
pod_name = check_output(b'kubectl get pod -o name', shell=True)[4:].rstrip()
check_output(
    b'kubectl exec '
    + pod_name
    + b' -- '
      b'bash -c "'
      b'. ~/www/python/venv/bin/activate '
      b'&& pip install -Ur requirements.txt'
      b'"',
    shell=True
)
check_output(b'webservice --backend=kubernetes python restart', shell=True)
