# Project Sentry

A Secure Authentication System built with Flask and Python
Project Sentry demonstrates modern cybersecurity practices including secure password hashing, rate limiting, and two-factor authentication (2FA).

# LINKS: 

[Security Documentation](https://docs.google.com/document/d/1hYRu6YhhjjTEuGHL9Sx6-9YC40kEh27Tz0SoEF7KZwU/edit?usp=sharing)

[Github](https://github.com/realahadkhan)

## Features:

User registration and login with password validation rules

Password hashing using bcrypt

Rate limiting for login attempts

Two-Factor Authentication (OTP) via console output

Clean and modern UI with responsive design

GitHub integration and security documentation link

Dashboard with project branding

## Images

<p align="center">
  <a href="register.png"><img src="register.png" width="300"></a>
  <a href="login.png"><img src="login.png" width="300"></a>
</p>

<p align="center">
  <a href="dashboard.png"><img src="dashboard.png" width="300"></a>
  <a href="securitydoc.png"><img src="securitydoc.png" width="300"></a>
</p>


## Getting Started

Follow these steps to run Project Sentry locally:

### Prerequisites

Python installed

Git installed


## Step 1: Clone the repository

git clone https://github.com/realahadkhan/project-sentry.git

## Step 2: Create a virtual environment

python -m venv venv

## Step 3: Activate the virtual environment

venv\Scripts\Activate  # For Windows Powershell

source venv/bin/activate # For Linux/Mac OS

## Step 4: Install dependencies

pip install -r requirements.txt

## Step 5: Run the application

python app.py

## Step 6: Access the system

http://127.0.0.1:5000/


# SECURITY NOTES

OTPs are printed to the console for demo purposes.

Database (users.db) stores usernames and hashed passwords.

Future updates may include email-based OTP delivery and session hardening.

