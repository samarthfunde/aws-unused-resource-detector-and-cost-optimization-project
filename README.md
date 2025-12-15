# AWS Unused Resource Detector & Cost Optimization

## 📌 Project Overview

The **AWS Unused Resource Detector & Cost Optimization** project is a serverless automation solution that scans an AWS account to identify unused or idle resources and sends cost optimization alerts via email. It also generates a CSV report and stores it in Amazon S3 for tracking and auditing purposes.

This project helps reduce unnecessary AWS billing by proactively identifying resources that are not actively in use.

---

## 🏗️ Architecture

**Flow:**

Amazon EventBridge (Scheduled Rule)
            │
            ▼
AWS Lambda (Unused Resource Detector)
            │
            ├── Scans AWS Account for Unused Resources
            │   (EC2, EBS, ELB, RDS, S3, etc.)
            │
            ├── Generates CSV Cost Optimization Report
            │
            ├── Stores CSV Report in Amazon S3
            │
            └── Publishes Notification to Amazon SNS
                        │
                        ▼
                Email Notification to User


---

## 🧰 AWS Services Used

* **Amazon EventBridge** – Schedules the Lambda execution (daily / periodic)
* **AWS Lambda** – Executes Python logic to detect unused resources
* **Amazon SNS** – Sends email notifications with cost-saving details
* **Amazon S3** – Stores generated CSV reports
* **AWS IAM** – Manages permissions securely
* **Amazon EC2 / RDS / ELB APIs** – Used for resource scanning

---

## 📂 Repository Structure

```
aws-unused-resource-detector/
│
├── lambda_function.py
├── unused_resources_2025-12-15.csv   # Sample output (for reference)
│
├── Snapshots_Of_Steps/
│   ├── Output/
│   │   ├── csv_report_3.jpeg
│   │   ├── csv_report_4.jpeg
│   │   ├── sns_mail_1.jpeg
│   │   └── sns_mail_2.jpeg
│   │
│   ├── Step_1_SNS_Create/
│   ├── Step_2_IAM_ROLE/
│   ├── Step_3_S3_Bucket/
│   ├── Step_4_Event_Bridge_Rule/
│   └── Step_5_Lambda/
│
└── README.md
```

---

## ⚙️ Step-by-Step Implementation

### Step 1️⃣: Create SNS Topic

* Create an SNS **Standard Topic**
* Add an **Email subscription** and confirm it

📸 Screenshots: `Snapshots_Of_Steps/Step_1_SNS_Create/`

---

### Step 2️⃣: Create IAM Role for Lambda

Attach the following **AWS Managed Policies**:

* AmazonEC2ReadOnlyAccess
* AmazonRDSReadOnlyAccess
* ElasticLoadBalancingReadOnlyAccess
* AmazonS3FullAccess
* AmazonS3ReadOnlyAccess
* AmazonSNSFullAccess
* CloudWatchReadOnlyAccess

📸 Screenshots: `Snapshots_Of_Steps/Step_2_IAM_ROLE/`

---

### Step 3️⃣: Create S3 Bucket

* Create an S3 bucket (example: `aws-unused-resource-reports`)
* Used to store CSV cost reports

📸 Screenshots: `Snapshots_Of_Steps/Step_3_S3_Bucket/`

---

### Step 4️⃣: Create EventBridge Rule

* Schedule rule (recommended: once per day)
* Target: Lambda function

📸 Screenshots: `Snapshots_Of_Steps/Step_4_Event_Bridge_Rule/`

---

### Step 5️⃣: Create Lambda Function

* Runtime: Python 3.x
* Timeout: 2 minutes
* Attach IAM role
* Deploy `lambda_function.py`

📸 Screenshots: `Snapshots_Of_Steps/Step_5_Lambda/`

---

## 🔍 Resources Detected

* Stopped EC2 Instances
* Unattached EBS Volumes (30+ days)
* Unused Elastic IPs
* Unattached Security Groups
* Unused Load Balancers
* Stopped RDS Instances

---

## 📄 CSV Report

* Generated automatically on each execution
* Stored in Amazon S3
* Contains:

  * Resource Type
  * Resource ID
  * Estimated Monthly Saving (INR)
  * Total Estimated Saving

📸 Output Screenshots: `Snapshots_Of_Steps/Output/`

---

## 📧 Email Notification (SNS)

The SNS email includes:

* List of unused resources
* Estimated monthly cost savings
* Recommendation to delete unused resources

---

## 💰 Cost Considerations

* Uses AWS Free Tier services
* Minimal cost for EventBridge & SNS
* S3 cost depends on stored CSV size

---

## 🔐 Security Best Practices

* No hardcoded AWS credentials
* IAM role-based access
* Principle of least privilege followed

---

## 🚀 Future Enhancements

* Automatic cleanup with approval
* Slack / Microsoft Teams notifications
* Cost Explorer API integration
* Terraform / CloudFormation deployment

---

## 🧑‍💻 Author

**Samarth Funde**
AWS Cloud & DevOps Engineer

---

## ⭐ Conclusion

This project demonstrates real-world AWS serverless automation for cost optimization. It is ideal for learning, cloud portfolios, and interview discussions.
