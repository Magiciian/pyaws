from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

# Configuration for AWS credentials

def get_ec2_client(region):
    return boto3.client('ec2', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def get_global_instance_counts():
    running_instances = 0
    stopped_instances = 0
    for region in AWS_REGION_NAMES:
        ec2 = get_ec2_client(region)
        response = ec2.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    running_instances += 1
                elif instance['State']['Name'] == 'stopped':
                    stopped_instances += 1
    return running_instances, stopped_instances

def get_resource_counts(region):
    ec2 = get_ec2_client(region)
    elb = boto3.client('elb', region_name=region, aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Fetch counts
    ami_count = len(ec2.describe_images(Owners=['self'])['Images'])
    volume_count = len(ec2.describe_volumes()['Volumes'])
    snapshot_count = len(ec2.describe_snapshots(OwnerIds=['self'])['Snapshots'])
    security_group_count = len(ec2.describe_security_groups()['SecurityGroups'])
    elastic_ip_count = len(ec2.describe_addresses()['Addresses'])
    load_balancer_count = len(elb.describe_load_balancers()['LoadBalancerDescriptions'])

    # Fetch instance data
    instance_data = []
    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_info = {
                'Server Name': next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                'vCPU': instance.get('CpuOptions', {}).get('CoreCount', 'N/A'),
                'RAM': instance.get('MemoryInfo', {}).get('SizeInMiB', 'N/A'),
                'HDD': instance.get('BlockDeviceMappings', [{}])[0].get('Ebs', {}).get('VolumeSize', 'N/A'),
                'Private IP': instance.get('PrivateIpAddress', 'N/A'),
                'Public IP': instance.get('PublicIpAddress', 'N/A'),
                'Owner': instance.get('OwnerId', 'N/A'),
                'Tags': ', '.join([f"{tag['Key']}: {tag['Value']}" for tag in instance.get('Tags', [])]),
                'State': instance['State']['Name']  # Added to capture the instance state
            }
            instance_data.append(instance_info)

    # Compute running and stopped instance counts
    running_instances = len([i for i in instance_data if i.get('State') == 'running'])
    stopped_instances = len([i for i in instance_data if i.get('State') == 'stopped'])

    return {
        'instance_data': instance_data,
        'ami_count': ami_count,
        'volume_count': volume_count,
        'snapshot_count': snapshot_count,
        'security_group_count': security_group_count,
        'elastic_ip_count': elastic_ip_count,
        'load_balancer_count': load_balancer_count,
        'running_instances': running_instances,
        'stopped_instances': stopped_instances
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    global_running_instances, global_stopped_instances = get_global_instance_counts()
    
    instance_data = []
    ami_count = volume_count = snapshot_count = security_group_count = elastic_ip_count = load_balancer_count = 0
    running_instances = stopped_instances = 0
    
    if request.method == 'POST':
        region = request.form.get('region')

        resource_data = get_resource_counts(region)
        instance_data = resource_data['instance_data']
        ami_count = resource_data['ami_count']
        volume_count = resource_data['volume_count']
        snapshot_count = resource_data['snapshot_count']
        security_group_count = resource_data['security_group_count']
        elastic_ip_count = resource_data['elastic_ip_count']
        load_balancer_count = resource_data['load_balancer_count']
        running_instances = resource_data['running_instances']
        stopped_instances = resource_data['stopped_instances']

    return render_template('dashboard.html', regions=AWS_REGION_NAMES,
                           global_running_instances=global_running_instances,
                           global_stopped_instances=global_stopped_instances,
                           instance_data=instance_data, ami_count=ami_count,
                           volume_count=volume_count, snapshot_count=snapshot_count,
                           security_group_count=security_group_count,
                           elastic_ip_count=elastic_ip_count,
                           load_balancer_count=load_balancer_count,
                           running_instances=running_instances,
                           stopped_instances=stopped_instances)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 

