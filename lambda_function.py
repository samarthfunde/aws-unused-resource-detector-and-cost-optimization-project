import boto3
from datetime import datetime, timezone
import csv
import io

# AWS clients
ec2 = boto3.client('ec2')
rds = boto3.client('rds')
elbv2 = boto3.client('elbv2')
s3 = boto3.client('s3')
sns = boto3.client('sns')

# CONFIG
DAYS = 30
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:610726994339:aws-unused-resource-alert"
REPORT_BUCKET = "aws-unused-resource-reports"

def lambda_handler(event, context):

    now = datetime.now(timezone.utc)
    report_rows = []   # for CSV
    email_lines = []   # for email
    total_saving = 0

    # =========================
    # EC2 – Stopped Instances
    # =========================
    instances = ec2.describe_instances()
    for r in instances['Reservations']:
        for i in r['Instances']:
            if i['State']['Name'] == 'stopped':
                email_lines.append(f"EC2 stopped: {i['InstanceId']}")
                report_rows.append(["EC2", i['InstanceId'], 0])

    # =========================
    # EBS – Unattached Volumes (30 days)
    # =========================
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    for v in volumes['Volumes']:
        age = (now - v['CreateTime']).days
        if age >= DAYS:
            cost = 800  # approx ₹ per month
            total_saving += cost
            email_lines.append(f"EBS unattached (>{DAYS} days): {v['VolumeId']} (~₹{cost})")
            report_rows.append(["EBS", v['VolumeId'], cost])

    # =========================
    # Elastic IP – Unattached
    # =========================
    addresses = ec2.describe_addresses()
    for eip in addresses['Addresses']:
        if 'InstanceId' not in eip:
            cost = 350
            total_saving += cost
            email_lines.append(f"Elastic IP unused: {eip['AllocationId']} (~₹{cost})")
            report_rows.append(["ElasticIP", eip['AllocationId'], cost])

    # =========================
    # Security Groups – Unattached
    # =========================
    sgs = ec2.describe_security_groups()['SecurityGroups']
    enis = ec2.describe_network_interfaces()['NetworkInterfaces']

    used_sg_ids = set()
    for eni in enis:
        for g in eni['Groups']:
            used_sg_ids.add(g['GroupId'])

    for sg in sgs:
        if sg['GroupId'] not in used_sg_ids and sg['GroupName'] != 'default':
            email_lines.append(f"Unused Security Group: {sg['GroupId']}")
            report_rows.append(["SecurityGroup", sg['GroupId'], 0])

    # =========================
    # Load Balancer – No Targets
    # =========================
    lbs = elbv2.describe_load_balancers()['LoadBalancers']
    for lb in lbs:
        tgs = elbv2.describe_target_groups(
            LoadBalancerArn=lb['LoadBalancerArn']
        )
        if not tgs['TargetGroups']:
            cost = 1300
            total_saving += cost
            email_lines.append(f"Load Balancer unused: {lb['LoadBalancerName']} (~₹{cost})")
            report_rows.append(["LoadBalancer", lb['LoadBalancerName'], cost])

    # =========================
    # RDS – Stopped
    # =========================
    dbs = rds.describe_db_instances()['DBInstances']
    for db in dbs:
        if db['DBInstanceStatus'] == 'stopped':
            cost = 1500
            total_saving += cost
            email_lines.append(f"RDS stopped: {db['DBInstanceIdentifier']} (~₹{cost})")
            report_rows.append(["RDS", db['DBInstanceIdentifier'], cost])

    # =========================
    # CREATE CSV (IN MEMORY)
    # =========================
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["ResourceType", "ResourceId", "EstimatedMonthlySaving(INR)"])

    for row in report_rows:
        writer.writerow(row)

    # Add total saving row at the end
    writer.writerow([])
    writer.writerow(["Total", "", total_saving])

    # Upload to S3
    s3.put_object(
        Bucket=REPORT_BUCKET,
        Key=f"reports/unused_resources_{now.date()}.csv",
        Body=csv_buffer.getvalue()
    )

    # =========================
    # SNS EMAIL
    # =========================
    if email_lines:
        message = (
            "Unused AWS Resources Detected (30+ days)\n\n"
            + "\n".join(email_lines)
            + f"\n\nEstimated Monthly Saving: ₹{total_saving}\n\n"
            + "Action: Please review and remove manually if not required."
        )
    else:
        message = "No unused AWS resources found."

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="AWS Cost Optimization Report",
        Message=message
    )

    return {
        "status": "success",
        "resources_found": len(report_rows),
        "estimated_saving": total_saving
    }
