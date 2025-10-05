# 🤖 Meeting Discord Bot

A Discord bot for managing team meetings with structured updates, progress tracking, and automated reporting.

## ✨ Features

- **Create Meetings**: Generate unique meeting IDs with `/meetingbot new`
- **Submit Updates**: Use interactive modals to submit progress, blockers, and goals
- **Close Meetings**: Lock meetings and prevent further updates with `/meetingbot close`
- **Data Validation**: All fields are required with 500-character limits
- **JSON Storage**: Local file-based storage during development
- **Rich Embeds**: Beautiful Discord embeds for all interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A Discord server where you can add bots
- Discord Developer Portal access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-discord-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Discord Bot**
   - Follow the detailed guide in [DISCORD_SETUP.md](DISCORD_SETUP.md)
   - Create a `.env` file with your bot token and guild ID

4. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Commands

### `/meetingbot new`
Creates a new meeting with a unique ID.

**Example:**
```
/meetingbot new
```

**Response:** Creates a meeting with ID like `a1b2c3d4` and shows creation details.

### `/meetingbot update <meeting_id>`
Opens an interactive modal form to submit meeting updates.

**Parameters:**
- `meeting_id` (required): The ID of the meeting to update

**Example:**
```
/meetingbot update a1b2c3d4
```

**Modal Fields:**
- **Progress** (required, max 500 chars): What you've accomplished
- **Blockers** (required, max 500 chars): What's blocking your progress
- **Goals** (required, max 500 chars): Your goals for the next period

### `/meetingbot close <meeting_id>`
Closes a meeting, preventing further updates.

**Parameters:**
- `meeting_id` (required): The ID of the meeting to close

**Example:**
```
/meetingbot close a1b2c3d4
```

**Response:** Shows meeting summary and locks the meeting.

## 🏗️ Project Structure

```
meeting-discord-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py          # Main Discord bot implementation
│   ├── models.py       # Data models (Meeting, Update)
│   └── storage.py      # JSON file storage system
├── json/               # Meeting data storage (auto-created)
├── templates/          # HTML templates (future use)
├── main.py            # Entry point
├── requirements.txt   # Python dependencies
├── .env.example      # Environment variables template
├── DISCORD_SETUP.md  # Discord bot setup guide
└── README.md         # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# AWS Configuration (for future S3 integration)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_S3_BUCKET=your_s3_bucket_name_here
```

### Data Storage

- **Development**: Meetings are stored as JSON files in `./json/<meeting_id>/meeting.json`
- **Future**: S3 integration for scalable storage

## 🛠️ Development

### Running in Development

1. **Start the bot**
   ```bash
   python main.py
   ```

2. **Test commands** in your Discord server

3. **View meeting data** in the `json/` directory

### Previewing the HTML Report Locally (No Bot, No S3)

You can iterate on the HTML template without running the bot or uploading to S3.

1. Ensure you have at least one local meeting JSON (from a bot run) under `json/<meeting_id>/meeting.json`.
   - Alternatively, copy an existing file and edit it for faster iteration.

2. Render the HTML report locally:
   ```bash
   python -m src.report_preview --input json/<meeting_id>/meeting.json --output preview.html
   ```

3. Open the generated file in a browser:
   ```bash
   xdg-open preview.html  # Linux
   open preview.html      # macOS
   start preview.html     # Windows
   ```

Changes to `templates/meeting_report.html` will be reflected the next time you run the command.

### Adding New Features

1. **New Commands**: Add to `src/bot.py` in the `@bot.tree.command` decorator
2. **Data Models**: Extend `src/models.py`
3. **Storage**: Modify `src/storage.py` for different storage backends

## 🔒 Security & Permissions

- **Bot Token**: Keep your Discord bot token secret
- **Guild Access**: Bot only works in the specified guild
- **User Access**: Anyone with server access can create/update meetings
- **Data Privacy**: Meeting data is stored locally (consider encryption for sensitive data)

## 🚧 Future Enhancements

- **S3 Integration**: Cloud storage for meeting data and reports
- **HTML Reports**: Generate beautiful meeting summaries
- **CSV Export**: Export meeting data to spreadsheets
- **Meeting Analytics**: Track progress over time
- **Role-based Permissions**: Restrict meeting management to specific roles
- **Scheduled Meetings**: Automatic meeting creation and reminders

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Check bot token in `.env` file
- Verify bot has proper permissions
- Ensure Message Content Intent is enabled

**Slash commands not appearing:**
- Restart the bot (commands sync on startup)
- Check guild ID is correct
- Verify bot is in the server

**Permission errors:**
- Ensure bot has "Use Slash Commands" permission
- Check bot is not rate-limited

### Getting Help

1. Check the [Discord Setup Guide](DISCORD_SETUP.md)
2. Review the console output for error messages
3. Verify your `.env` file configuration

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Happy Meeting! 🎉**