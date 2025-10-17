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
- Discord account

### Installation

You can run the bot after cloning the bot, creating a Discord app and AWS infrastructure, and filling out the environment variables

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

### Previewing the HTML Report Locally (No Bot, No S3)

You can iterate on the HTML template without running the bot or uploading to S3.

1. Ensure you have at least one local meeting JSON (from a bot run) under `json/<meeting_id>/meeting.json`.
   - Alternatively, copy an existing file and edit it for faster iteration.

2. Render the HTML report locally:
   ```bash
   python -m src.report_preview --input json/<meeting_id>/meeting.json --output preview.html
   ```

3. Open the generated file in a browser:

### Getting Help

1. Check the [Discord Setup Guide](DISCORD_SETUP.md)
2. Review the console output for error messages
3. Verify your `.env` file configuration

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
