#!/usr/bin/python

# -*- coding: utf-8 -*-

import sys,time,datetime

def getNova(tenancy):

	d={}
	d['username'] = 'admin'
	d['api_key'] = 'keystone_admin'
	d['auth_url'] = 'http://localhost:5000/v2.0'
	d['project_id'] = '40a9b830f50b4f5d9d7780f6b73aa4ee'
	d['tenant_id']= tenancy

	from novaclient.v1_1 import client
	#from credentials import get_nova_creds
	creds = d
	nova = client.Client(**creds)

	return nova


def getDBdata():

	gettenancy_sql="select default_project_id from keystone.user where name='admin'"
	tenancy=''
	getcomputehostnames_sql="select hypervisor_hostname from nova.compute_nodes;"
	#getcomputehostnames_sql="select name from test55.pet;"
	comphosts=[]

	import MySQLdb as mdb
	import MySQLdb.cursors

	#con = mdb.connect(host='localhost', user='root',cursorclass=MySQLdb.cursors.DictCursor)
	con = mdb.connect(host='localhost', user='root')

	with con: 

	    cur = con.cursor()
	    cur.execute(gettenancy_sql)

	    rows = cur.fetchall()

	    #print rows
	    tenancy=rows[0][0]

	    cur.execute(getcomputehostnames_sql)
	    rowhosts=cur.fetchall()

	    for x in rowhosts:
		comphosts.append(x[0])
	    
	    #compute_hostnames=rowhosts[0][0]

	
	return [tenancy,comphosts]





def doesImageExist(name):

	#nova.images.find(name='debian-test1')


	for x in nova.images.list():
		print x.name
		if x.name==name:
			return True
		else:
			return False



def uploadImage(imagepath,name):

	keystonecreds={}
	keystonecreds['username'] = 'admin'
	keystonecreds['password'] = 'keystone_admin'
	keystonecreds['auth_url'] = 'http://localhost:5000/v2.0'
	keystonecreds['tenant_name'] = 'admin'


	import keystoneclient.v2_0.client as ksclient
	import glanceclient
	keystone = ksclient.Client(**keystonecreds)

	glance_endpoint = keystone.service_catalog.url_for(service_type='image',
							   endpoint_type='publicURL')

	glance = glanceclient.Client('1',glance_endpoint, token=keystone.auth_token)
	with open(imagepath) as fimage:
		glance.images.create(name=name, is_public=True, disk_format="qcow2",
			container_format="bare", data=fimage)


def createInstance(name,hypervisorhost):

	serverstatus=None

	print nova.security_groups.list()
	print nova.images.list()
	image = nova.images.find(name="cirros-0.3-x86_64")
	flavor = nova.flavors.find(name="m1.tiny")
	print nova.networks.list()
	network = nova.networks.find(label="novanetwork")

#   keypair works - need to add key-gen
#	f = open('/root/.ssh/id_rsa.pub','r')
#	publickey = f.readline()[:-1]
	#keypair = nova.keypairs.create('openstack-unittest',publickey)

#	keypair=nova.keypairs.find(name='openstack-unittest')
#	print nova.keypairs.list()


	#help(nova.servers.create)
	
	server = nova.servers.create(name = name,
					 image = image.id,
					 flavor = flavor.id,
					 network = network.id,
#					 key_name = keypair.name,
					 availability_zone='nova:'+ hypervisorhost
					 )
	

	print server
     
	print server.status

	testtimes=15

	while True:
		fserver=nova.servers.find(id=server.id)
		print fserver
		if fserver.status=='ACTIVE':
			serverstatus=0
			break
		if fserver.status=='ERROR':
			serverstatus=1
			break
				
		time.sleep(2)
		testtimes -= 1		
		if testtimes==0:
			serverstatus=1
			break

	server.delete()
	

	
	return serverstatus,server
 

	#nova.images.find(name='debian-test1')



imagename='cirros-0.3-x86_64'
imagepath='/opt/hibu/bin/cirros-0.3.0-x86_64-disk.img'

tenancy,serverlist=getDBdata()


nova=getNova(tenancy)

if not doesImageExist(imagename):
	uploadImage(imagepath,imagename)

print serverlist

#sys.exit(0)

errorcode=0
ret=[]

for s in serverlist:

	ts = time.time()	
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')	
	name='unit-test-'+st+'-'+s

	serverstatus,server=createInstance(name,s)
	ret.append([serverstatus,server])
	time.sleep(2)

for x in ret:
	serverstatus,server=x
	errorcode += serverstatus
	print serverstatus,server

print errorcode
if errorcode > 0:
	sys.exit(1)





"""
server = nova.servers.create(name = "debian-test-key",
                                 image = image.id,
                                 flavor = flavor.id,
                                 network = network.id,
				 key_name = keypair.name
                                 )
"""


'''
import keystoneclient.v2_0.client as ksclient
import glanceclient
keystone = ksclient.Client(**keystonecreds)

glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')

glance = glanceclient.Client('1',glance_endpoint, token=keystone.auth_token)
with open('/root/cirros-0.3.0-x86_64-disk.img') as fimage:
	glance.images.create(name="cirros", is_public=True, disk_format="qcow2",
		container_format="bare", data=fimage)



try: 
	#if nova.images.find(name='debian-test1')
        print boolean(nova.images.find(name='cirros-0.3-x86_64'))

#import Novaclient

except NotFound:
	cirrus_image_exists=False	
"""
'''

'''

t="""
export OS_AUTH_URL=http://172.30.0.82:5000/v2.0

# With the addition of Keystone we have standardized on the term **tenant**
# as the entity that owns the resources.
export OS_TENANT_ID=%s
export OS_TENANT_NAME="admin"

# In addition to the owning entity (tenant), openstack stores the entity
# performing the action as the **user**.
export OS_USERNAME="admin"

export OS_PASSWORD=keystone_admin

wget https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
name=cirros-0.3-x86_64
image=cirros-0.3.0-x86_64-disk.img
glance image-create --name=$name --is-public=true --container-format=bare --disk-format=qcow2 < $image
nova image-list

nova boot --image cirros-0.3-x86_64 --flavor m1.tiny --key_name test  myfouthserver
nova list

""" % tenancy

"""

fd=file('output.sh','w')

for line in t:
        fd.write(line)

fd.close()
"""
'''