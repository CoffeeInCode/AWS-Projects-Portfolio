# AWS Two-Tier To-Do Web Application

## Overview

This project demonstrates the deployment of a scalable and resilient two-tier web application on Amazon Web Services (AWS). The application is a simple To-Do List manager, built with Node.js and Express.js for the backend, and utilizing a MySQL database hosted on Amazon RDS. The primary goal was to implement a robust cloud architecture focusing on high availability, security, and best practices for cloud deployment.

---

## Architecture

The application follows a classic two-tier architecture:

* **Web Tier:** Two Amazon EC2 instances host the Node.js application. These instances are distributed across two Availability Zones (AZs) for high availability. An Application Load Balancer (ALB) distributes incoming user traffic evenly across these instances.
* **Database Tier:** An Amazon RDS for MySQL instance stores the application data. This database is deployed in private subnets across two Availability Zones (Multi-AZ recommended for production, single-AZ for cost-effective demo) for data durability and high availability, isolated from direct internet access.

**Diagram:**

*(Please insert your architecture diagram image here. You can upload it to your GitHub repo and link it like this: `![Architecture Diagram](architecture-diagram.png)`)*

**Traffic Flow:**
User Request -> Internet -> Application Load Balancer (Public Subnets) -> EC2 Instances (Node.js App in Public Subnets) -> RDS MySQL Instance (Private Subnets)

---

## Key Features & Design Choices

* **High Availability:**
    * EC2 instances deployed across multiple Availability Zones.
    * Application Load Balancer for traffic distribution and health checks.
    * RDS instance (optionally Multi-AZ) for database resilience.
* **Scalability:** The architecture supports horizontal scaling of the EC2 instances behind the ALB.
* **Security:**
    * Custom VPC for network isolation.
    * Public subnets for web-facing resources (ALB, EC2) and private subnets for the RDS database.
    * Security Groups meticulously configured to allow only necessary traffic between tiers (ALB <-> EC2, EC2 <-> RDS).
    * IAM roles for EC2 instances to provide secure access to AWS services (e.g., Systems Manager for SSH-less access).
    * Database credentials managed via environment variables on EC2 instances (for production, AWS Secrets Manager would be preferred).
* **Networking:**
    * Custom VPC with a `/16` CIDR block.
    * Separate public and private route tables.
    * Internet Gateway (IGW) for outbound internet access from public subnets.
    * NAT Gateway for outbound internet access from private subnets if needed by RDS or other private resources.

---

## Technologies Used & AWS Services

* **Application:** Node.js, Express.js
* **Database:** MySQL
* **AWS Services:**
    * **Amazon EC2 (Elastic Compute Cloud):** Hosts the Node.js application servers.
    * **Amazon RDS (Relational Database Service):** Managed MySQL database.
    * **Application Load Balancer (ALB):** Distributes incoming application traffic.
    * **Amazon VPC (Virtual Private Cloud):** Isolated cloud network.
        * Subnets (Public & Private)
        * Route Tables
        * Internet Gateway (IGW)
        * NAT Gateway
    * **IAM (Identity and Access Management):** Securely manages access to AWS services.
    * **Security Groups:** Stateful firewall for controlling instance traffic.
    * **AWS CLI:** Used for scripting and automating resource creation (alongside AWS Management Console).
* **Process Management:** PM2 for managing the Node.js application on EC2.

---

## Setup & Deployment Highlights

1.  **VPC & Networking:** Established a custom VPC, public/private subnets across two AZs, configured route tables, IGW, and NAT Gateway.
2.  **Database Deployment:** Launched an RDS MySQL instance within private subnets, configured a DB subnet group, and secured it with a dedicated security group allowing access only from EC2 instances.
3.  **Application Server Setup:**
    * Launched two EC2 instances in public subnets.
    * Utilized user data scripts for initial setup (installing Node.js, NVM, PM2, Git).
    * Deployed the Node.js To-Do application code.
    * Configured environment variables (`.env` file) on each EC2 instance for database connection details.
4.  **Load Balancing:** Configured an Application Load Balancer to distribute traffic to the EC2 instances and perform health checks.
5.  **Security Configuration:** Implemented security groups for ALB, EC2, and RDS, ensuring least-privilege access between tiers.

---

## What I Learned / Skills Demonstrated

* **Cloud Architecture Design:** Designing a resilient, scalable, and secure two-tier application on AWS.
* **AWS Core Services:** Hands-on experience with VPC, EC2, RDS, ALB, IAM, and Security Groups.
* **Networking on AWS:** Deep understanding of subnets, route tables, IGWs, NAT Gateways.
* **Security Best Practices:** Implementing network segmentation, security groups, IAM roles, and considerations for secret management.
* **Application Deployment & Management:** Deploying a Node.js application on EC2, using PM2 for process management, and configuring environment variables.
* **Troubleshooting:** Diagnosing connectivity and configuration issues across different AWS services.
* **High Availability Concepts:** Implementing solutions that ensure application uptime across multiple Availability Zones.

---

*This project was built from scratch to solidify understanding of fundamental AWS services and best practices for cloud application deployment.*
