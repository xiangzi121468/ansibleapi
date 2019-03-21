#!/usr/bin/python
#coding=utf-8
##下面是callbackbase  改写
##下面先引用InventoryManager  VariableManager 包
from ansible.parsing.dataloader  import DataLoader
from ansible.inventory.manager  import InventoryManager
from ansible.vars.manager  import VariableManager
from ansible.playbook.play  import Play
from collections import namedtuple
from ansible.executor.task_queue_manager  import TaskQueueManager
from ansible.plugins.callback import CallbackBase
#实例化类并且指定好资产的地址
loader = DataLoader()
Inventory = InventoryManager(loader=loader,sources=['/etc/ansible/hosts'])
variable_manager=VariableManager(loader=loader,inventory=Inventory)
#Options 执行选项
#先定义Options 类属性
Options= namedtuple('Options',
                      ['connection',
                      'remote_user',
                      'ask_sudo_pass',
                      'verbosity',
                      'ack_pass',
                      'module_path',
                      'forks',
                      'become',
                      'become_method',
                      'become_user',
                      'check',
                      'listhosts',
                      'listtasks',
                      'listtags',
                      'syntax',
                      'sudo_user',
                      'sudo',
                      'diff'])
#实例化Options传入参数
options= Options(connection='smart',
                   remote_user=None,
                   ack_pass=None,
                   sudo_user=None,
                   forks=5,
                   sudo=None,
                   ask_sudo_pass=False,
                   verbosity=5,
                   module_path=None,
                   become=None,
                   become_method=None,
	               become_user=None,
                   check=False,
                   diff=False,
                   listhosts=None,
                   listtasks=None,
                   listtags=None,
                   syntax=None
                )

#play 执行对象和模块
class ModelResultsCollector(CallbackBase):
    """重写callbackBase类的部分方法"""

    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.hosk_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.hosk_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result,  *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


callback = ModelResultsCollector()
play_source = dict(
              name = "ansible  脚本  命令 test",
              hosts= 'k8snode',
              gather_facts ='no',
              tasks=[
                     dict(action=dict(module='shell',args='ls /root'),register='shell_out')
                    ]
              )
play = Play().load(play_source,variable_manager=variable_manager,loader=loader)
#定义
passwords= dict()
tqm =TaskQueueManager(
               inventory=Inventory,
               variable_manager=variable_manager,
               loader=loader,
               options=options,
               passwords=passwords,
               stdout_callback=callback
                )
result = tqm.run(play)
#print  callback.hosk_ok.items()
result_raw= {'success':{},'failed':{},'unreachable':{}}
for  host,result  in  callback.hosk_ok.items():
     result_raw['success'][host]=result._result
"""for  host,result  in  callback.hosk_unreachable.items():
     result_raw['unreachable'][host]=result._result
"""
print  result_raw