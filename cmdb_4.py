#!/usr/bin/env/python
#coding=utf-8
##这边是调用的playbook 模式
##下面先引用InventoryManager  VariableManager 包
from ansible.parsing.dataloader  import DataLoader
from ansible.inventory.manager  import InventoryManager
from ansible.vars.manager  import VariableManager
from ansible.executor.playbook_executor  import PlaybookExecutor
from ansible.playbook.play  import Play
from collections import namedtuple
from ansible.plugins.callback import CallbackBase
#from ansible.executor.task_queue_manager  import TaskQueueManager
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
#CallbackBase 改写
class  PlayBookResultCollector(CallbackBase):
      CALLBACK_VERSION  =2.0
      def  __init__(self,*args,**kwargs):
          super(PlayBookResultCollector,self).__init__(*args,**kwargs)
          self.task_ok ={}
          self.task_skipped= {}
          self.task_failed={}
          self.task_status={}
          self.task_unreachable={}
      def  v2_runner_on_ok(self, result):
          self.task_ok[result._host.get_name()]  = result

      def v2_runner_on_skipped(self, result):
          self.task_skipped[result._host.get_name()] = result

      def v2_runner_on_unreachable(self, result):
          self.task_unreachable[result._host.get_name()] = result
      def  v2_runner_on_failed(self, result, ignore_errors=False):
          self.task_failed[result._host.get_name()] = result
      def   v2_runner_on_stats(self,result):
            self.task_status[result._host.get_name()] = result
#实例化 PlayBookResultCollector
callback= PlayBookResultCollector()

#定义playbook
passwords= dict()
playbook  =PlaybookExecutor(playbooks=['f1.yml'],
                            inventory=Inventory,
                            variable_manager=variable_manager,
                            loader=loader,
                            options=options,
                            passwords=passwords
                            )
playbook._tqm._stdout_callback= callback
playbook.run()
#自定义输出的格式
results_raw={'skipped':{},'ok':{},'status':{},'failed':{},'unreachable':{}}
for  host, result  in callback.task_ok.items():
     results_raw['ok'][host] =result
"""
for  host, result  in callback.task_status.items():
     results_raw['status'][host] =result
for  host, result  in callback.task_skipped.items():
     results_raw['skipped'][host] =result
for  host, result  in callback.task_failed.items():
     results_raw['failed'][host] =result
for  host, result  in callback.task_unreachable.items():
     results_raw['unreachable'][host] =result
"""
print results_raw