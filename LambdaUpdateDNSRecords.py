	import boto3
	import re
	import uuid
	import time
	import random
	import os
	import logging
	from datetime import datetime

	print('Loading function ' + datetime.now().time().isoformat())
	route53 = boto3.client('route53')
	ec2 = boto3.resource('ec2')
	compute = boto3.client('ec2')
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	VERSION = '0.0.1'


	def lambda_handler(event, context):
		print(event)
		# Set variables
		zone_name = "mydomain123.com"
		zone_id = "Z123456789"
		domains = ["node123", "node456"]
		# Get the state
		state = event['detail']['state']
		instance_id = event['detail']['instance-id']
		region = event['region']
		instance = compute.describe_instances(InstanceIds=[instance_id])
		instance.pop('ResponseMetadata')

		try:
			tags = instance['Reservations'][0]['Instances'][0]['Tags']
		except:
			tags = []

		try:
			public_dns_name = instance['Reservations'][0]['Instances'][0]['PublicDnsName']
		except BaseException as e:
			print('Instance has no public IP or host name', e)

		print(public_dns_name)

		for domain in domains:
			if os.environ[domain] == instance_id:
				try:
					create_record(zone_id, domain, zone_name, 'CNAME', public_dns_name)
				except BaseException as e:
					print(e)
				try:
					create_record(zone_id, "*." + domain, zone_name, 'CNAME', public_dns_name)
				except BaseException as e:
					print(e)

	def create_record(zone_id, host_name, hosted_zone_name, type, value):
		if host_name[-1] != '.':
			host_name = host_name + '.'
		route53.change_resource_record_sets(
			HostedZoneId=zone_id,
			ChangeBatch={
				"Comment": "Updated by Lambda DDNS",
				"Changes": [
					{
						"Action": "UPSERT",
						"ResourceRecordSet": {
							"Name": host_name + hosted_zone_name,
							"Type": type,
							"TTL": 60,
							"ResourceRecords": [
								{
									"Value": value
								},
							]
						}
					},
				]
			}
		)