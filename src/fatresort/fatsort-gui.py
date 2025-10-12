#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# (c) 2008 by Alexander Schier
import subprocess
import os

lang="c"
if "LANG" in os.environ:
	lang=os.environ['LANG'].lower().split("_")[0]

strings={
"de": 
	{
	'Please choose the device, on which the files should be sorted.':
		'Waehlen Sie das Gerät auf dem die Dateien sortiert werden sollen.',
	'Device':
		'Gerät',
	'Size':
		'Größe',
	'files sucessfully sorted.':
		'Dateien erfolgreich sortiert.',
	'error while sorting the files!':
		'Fehler beim Sortieren der Dateien!',
	},
}

def _(string):
	if strings.has_key(lang) and strings[lang].has_key(string):
		return strings[lang][string]
	else:
		return string

def formatSize(size):
	size=float(size)
	if size > 1024*1024*1024:
		return "%.3f GB" % (size/(1024*1024*1024.0))
	elif size > 1024*1024:
		return "%.3f MB"%(size/(1024*1024.0))
	else:
		return "%d Byte"%size

outin=subprocess.Popen("hal-device", stderr=subprocess.PIPE, stdout=subprocess.PIPE)

data = outin.stdout.read()

devices=data.split("\n\n")
fatdevices=[]
for device in devices:
	if "volume.fstype = 'vfat'" in device:
		label=""
		dev=""
		mounted=True
		size=0
		for line in device.split("\n"):
			tmp=line.split("=", 1)
			if(tmp[0].strip()=="block.device"):
				dev=tmp[1].strip().split("'")[1] #i.e. " '/dev/sdb1'  (string)"
			elif tmp[0].strip()=="volume.label":
				label=tmp[1].strip().split("'")[1]
			elif tmp[0].strip()=="volume.is_mounted":
				mounted=(tmp[1].strip().split(" ")[0]!="false")
			elif tmp[0].strip()=="volume.size":
				size=tmp[1].strip().split(" ")[0]
		if dev!="":
			fatdevices.append((dev, label, formatSize(size), mounted))
options='--list --text "'+_('Please choose the device, on which the files should be sorted.')+'" --column="'+_('Device')+'" --column="'+_('Label')+'" --column="'+_("Size")+'"'
for fatdevice in fatdevices:
	if not fatdevice[3]:
		options+=' "%s" "%s" "%s"'%(fatdevice[0], fatdevice[1], fatdevice[2])
cmd = zenity + options.split(" ")
tmp=subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
#tmp=popen2.popen2("zenity %s"%options)
device = outin.stdout.read().strip()

#device=tmp[0].read().strip()
if device!="":
	if(os.system('fatsort "%s"'%device)==0):
		os.system('zenity --info --text="'+_('files sucessfully sorted.')+'"')
	else:
		os.system('zenity --error --text="'+_('error while sorting the files!')+'"')
