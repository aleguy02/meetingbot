# Discord Bot Setup Guide

This guide will walk you through setting up a Discord bot for the Meeting Bot application.

## Step 1: Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Enter a name for your bot (e.g., "Meeting Bot")
4. Click **"Create"**

## Step 2: Create a Bot User

1. In your application dashboard, go to the **"Bot"** section in the left sidebar
2. Click **"Add Bot"**
3. Click **"Yes, do it!"** to confirm
4. You'll see a bot user has been created

## Step 3: Get Bot Token

1. In the **"Bot"** section, find the **"Token"** section
2. Click **"Copy"** to copy your bot token
3. **⚠️ IMPORTANT: Keep this token secret! Never share it publicly.**

## Step 4: Set Bot Permissions

1. In the **"Bot"** section, scroll down to **"Privileged Gateway Intents"**
2. Enable the following intents:
   - ✅ **Message Content Intent** (required for slash commands)

## Step 5: Get Guild ID

1. In Discord, go to **User Settings** (gear icon) → **Advanced**
2. Enable **"Developer Mode"**
3. Right-click on your server name and select **"Copy Server ID"**
4. This is your Guild ID

## Step 6: Invite Bot to Server

1. In the Discord Developer Portal, go to **"OAuth2"** → **"URL Generator"**
2. Select **"bot"** in the **Scopes** section
3. In **Bot Permissions**, select:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and click **"Authorize"**

## Step 7: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your credentials:
   ```
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_GUILD_ID=your_guild_id_here
   ```

## Step 8: Install Dependencies and Run

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the bot:
   ```bash
   python -m src.bot
   ```

## Step 9: Test the Bot

Once the bot is running, you should see:
- A message in the console confirming the bot is connected
- Slash commands should be available in your Discord server

Try these commands:
- `/meetingbot new` - Create a new meeting
- `/meetingbot update <meeting_id>` - Add an update to a meeting
- `/meetingbot close <meeting_id>` - Close a meeting

## Troubleshooting

### Bot Not Responding
- Check that the bot token is correct in your `.env` file
- Ensure the bot has the necessary permissions in your server
- Verify the Guild ID is correct

### Slash Commands Not Appearing
- Make sure you've enabled **Message Content Intent** in the Discord Developer Portal
- Try restarting the bot - slash commands are synced on startup
- Check that the bot has the "Use Slash Commands" permission

### Permission Errors
- Ensure the bot has been invited with the correct permissions
- Check that the bot has access to the channels where you're testing

## Security Notes

- Never commit your `.env` file to version control
- Keep your bot token secret
- Consider using environment variables in production instead of `.env` files
- Regularly rotate your bot token if compromised

## Next Steps

Once your bot is running successfully, you can:
1. Customize the bot's appearance and behavior
2. Add more features like meeting reports
3. Deploy the bot to a cloud service for 24/7 operation

