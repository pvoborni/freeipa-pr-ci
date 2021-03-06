import os
import pytest

from .ansible import AnsiblePlaybook
from .common import PopenTask, TimeoutException, TaskException
from .vagrant import VagrantBoxDownload


def test_timeout():
    PopenTask(['sleep', '0.1'])()
    PopenTask(['sleep', '0.1'], timeout=None)()
    PopenTask(['sleep', '0.1'], timeout=0.2)()

    task = PopenTask(['sleep', '0.1'], timeout=0.01)
    with pytest.raises(TimeoutException) as exc_info:
        task()
    assert exc_info.value.task == task


def test_fallible_task():
    task = PopenTask(['ls', '/tmp/ag34feqfdafasdf'])
    with pytest.raises(TaskException) as exc_info:
        task()
    assert exc_info.value.task == task
    assert task.returncode != 0

    task = PopenTask(['ls', '/tmp/ag34feqfdafasdf'], raise_on_err=False)
    task()
    assert task.returncode != 0


def test_popen():
    task = PopenTask(['ls', '/tmp'])
    task()
    assert task.returncode == 0

    task = PopenTask(['ls', '/tmp/adsdasafgsag'], raise_on_err=False)
    task()
    assert task.returncode == 2

    PopenTask('for i in `seq 3`; do echo $i; done', shell=True)()

    task = PopenTask('ls /tmp/$DIR', shell=True, raise_on_err=False)
    task()
    assert task.returncode == 0

    env = dict(DIR='gfdsgsdfgsfd')
    task = PopenTask('ls /tmp/$DIR', shell=True, env=env, raise_on_err=False)
    task()
    assert task.returncode == 2


def test_vagrant_box_download():
    path = os.path.dirname(os.path.realpath(__file__))
    task = VagrantBoxDownload(
        vagrantfile='Vagrantfile.mock',
        path=path)
    vagrantfile = task.get_vagrantfile()

    assert vagrantfile.vm.box == 'freeipa/ci-master-f25'
    assert vagrantfile.vm.box_version == '0.2.5'


def test_ansible_playbook():
    assert ' '.join(
        AnsiblePlaybook(playbook='a.yml', inventory='hosts.test').cmd
        ) == 'ansible-playbook -i hosts.test a.yml'

    assert ' '.join(
        AnsiblePlaybook(playbook='a.yml', inventory='hosts.test',
                        extra_vars={'a': 1, 'b': 'xyz'}, verbosity='vvv').cmd
        ) == 'ansible-playbook -i hosts.test -e b=xyz -e a=1 a.yml -vvv'

    with pytest.raises(TaskException):
        AnsiblePlaybook()
