#!/usr/bin/python
# -*- coding:UTF-8 -*-
'''
auto publish tool
'''
import sys
import os
import json
import time
import zipfile

from fabric.api import cd, lcd, env
from fabric.operations import put, run

class ConfigUtil(object):

	def __init__(self):
		self.config_path = 'publish.json'
		self.config = {
						"server_list":[
							{"host": "", "user": "", "pwd": ""}
						],
						"upload_list":[
							{"local_path": "", "server_path": ""}
						],
						"befor_upload_cmd":[
							""
						],
						"after_upload_cmd":[
							""
						]
					}

	def initConfig(self):
		if os.path.exists(self.config_path):
			text = self.read(self.config_path)
			self.config = json.loads(text)
			if not self.verifyConfig():
				print '请在 %s 中配置相关参数' % self.config_path
				return (-1, self.config)
			return (0, self.config)
		else:
			self.write(self.config_path, json.dumps(self.config))
			print '请在 %s 中配置相关参数' % self.config_path
			return (-1, self.config)
		
	def verifyConfig(self):
		if not self.config:
			return False
		if self.config['server_list'] and len(self.config['server_list'])>0 and self.config['server_list'][0]['host']:
			return True

	def read(self, file):
		text = ''
		if os.path.exists(file):
			file_object = None
			try:
				file_object = open(file)
				text = file_object.read()
			finally:
				if file_object != None:
					file_object.close()
		return text

	def write(self, file, text):
		file_object = open(file, 'w')
		try:
			file_object.write(text)
		finally:
			file_object.close()

def make_zip(source_dir, output_filename):
	zipf = zipfile.ZipFile(output_filename, 'w')
	pre_len = len(os.path.dirname(source_dir))
	for parent, dirnames, filenames in os.walk(source_dir):
		for filename in filenames:
		  pathfile = os.path.join(parent, filename)
		  arcname = pathfile[pre_len:].strip(os.path.sep)   #相对路径
		  zipf.write(pathfile, arcname)
	zipf.close()

def scanDir(upload_list):
	for item in upload_list:
		if item['server_path'] and item['local_path']:
			tmp_file = 'publish.zip'
			make_zip(item['local_path'], tmp_file)
			# put('publish.zip', item['server_path'], use_sudo=True)
			put(tmp_file, item['server_path'])
			with cd(item['server_path']):
				run('unzip -o %s' % tmp_file)
				run('rm %s' % tmp_file)
			os.remove(tmp_file)

def executCmd(cmds):
	if not cmds:
		return
	for cmd in cmds:
		run(cmd)

def beforPublish(cmds):
	executCmd(cmds)

def afterPublished(cmds):
	executCmd(cmds)

def printAuthor():
	print "*********************************************************"
	print "***************** AUTO PUBLISH TOOL *********************"
	print "****************   author: Jane   ***********************"
	print "************* update: 2017-09-01 10:00:00 ***************"
	print "*********************************************************"

def main():
	current_path = sys.path[0]
	print current_path
	config_util = ConfigUtil()
	(status, config) = config_util.initConfig()
	if status == -1:
		return
	for item in config['server_list']:
		t = time.time()
		env.host_string = item['host']
		env.user = item['user']
		env.password = item['pwd']
		beforPublish(config['befor_upload_cmd'])
		scanDir(config['upload_list'])
		afterPublished(config['after_upload_cmd'])
		print '-' * 45
		print 'PUBLISH SUCCESS SPEED TIME : %ss' % (time.time() - t)
		print '-' * 45

if __name__ == '__main__':
	printAuthor()
	try:
		main()
	except Exception, e:
		print e
	os.system('rm publish.py')

