# 🤖 Meeting Discord Bot

A Discord bot for managing team meetings with structured updates, progress tracking, and automated reporting.

## ✨ Features

- **Create Meetings**: Generate unique meeting IDs with `/meetingbot new`
- **Submit Updates**: Use interactive modals to submit progress, blockers, and goals with `/meetingbot update`
- **Close Meetings**: Lock meetings and prevent further updates with `/meetingbot close`
- **Meeting Summary Static Site**: Closing a meeting automatically generates a static web page with all attendees' updates that you can share via an S3 presigned url

## 🚀 Quick Start

### Prerequisites

- Python 3.13.x
- Discord account and [Discord application](https://discord.com/developers/docs/intro)
- Non-root AWS account
- AWS CLI

### Development

The only infrastructure required for local development is an S3 bucket. You can create it manually or comment out the other resources in the terraform file for development (preferred because the configuration will be done for you). After creating the S3 bucket, copy example.env into a file named .env and fill out the variables.

**Run the bot with Python**

```bash
pip install -r requirements.txt
python main.py
```

**Run the bot with Docker**

```bash
docker build -t meetingbot .
docker run -v "$PWD/json":/meetingbot/json meetingbot:latest
```

### Deployment

Ironically, deployment is even easier. The only prerequisite is to create an EC2 key pair named "aws-ec2-key-pair" and download the private key. First, configure your AWS credentials with `aws configure` in the command line. Then, do the following commands to provision your infrastructure.

```bash
terraform init
terraform plan -out tfplan
terraform apply "tfplan"
```

You will be prompted to fill out some variables. You can read their descriptions in variables.tf. Your bot should be running in your servers after a couple of minutes!

### Previewing the HTML Report Locally (No Bot, No S3)

You can iterate on the HTML template without running the bot or uploading to S3.

1. Ensure you have at least one local meeting JSON (from a bot run) under `json/<meeting_id>/meeting.json`.

   - Alternatively, copy an existing file and edit it for faster iteration.

2. Render the HTML report locally:

   ```bash
   python -m src.report_preview --input json/<meeting_id>/meeting.json --output preview.html
   ```

3. Open the generated file in a browser:

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
