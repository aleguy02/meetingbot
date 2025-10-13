"""
Main Discord bot implementation for the meeting bot.
"""
import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from typing import Optional

from .models import Meeting, Update
from .storage import MeetingStorage
from .s3_storage import S3Storage
from .report_generator import ReportGenerator


class MeetingBot(commands.Bot):
    """Main bot class for handling meeting commands."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.storage = MeetingStorage()
        self.s3_storage = None  # Will be initialized after load_dotenv()
        self.report_generator = ReportGenerator()
        self.guild_id = None
    
    def initialize_s3(self):
        """Initialize S3 storage after environment is loaded."""
        if self.s3_storage is None:
            self.s3_storage = S3Storage()
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        # Initialize S3 storage (dotenv already loaded in main())
        self.initialize_s3()

        # Resolve guild IDs: prefer DISCORD_GUILD_IDS (comma-separated),
        # fall back to DISCORD_GUILD_ID, otherwise sync globally
        env_multi = os.getenv('DISCORD_GUILD_IDS', '')
        guild_ids = [int(g.strip()) for g in env_multi.split(',') if g.strip()]

        fallback_gid = os.getenv('DISCORD_GUILD_ID')
        if not guild_ids and fallback_gid:
            try:
                guild_ids = [int(fallback_gid)]
            except ValueError:
                print("Warning: DISCORD_GUILD_ID is not a valid integer; will sync globally")

        if guild_ids:
            # Per-guild sync for instant availability in each server
            for gid in guild_ids:
                guild = discord.Object(id=gid)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
            print(f"Synced slash commands for guilds: {guild_ids}")
        else:
            # Global sync (may take up to ~1 hour to propagate)
            await self.tree.sync()
            print("Synced global slash commands")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        
        print(f"Command error: {error}")
        await ctx.send(f"An error occurred: {str(error)}")


# Create bot instance
bot = MeetingBot()


@bot.tree.command(name="meetingbot", description="Meeting bot commands")
@app_commands.describe(action="Action to perform", meeting_id="Meeting ID (for update/close)")
@app_commands.choices(action=[
    app_commands.Choice(name="new", value="new"),
    app_commands.Choice(name="update", value="update"),
    app_commands.Choice(name="close", value="close")
])
async def meetingbot_command(interaction: discord.Interaction, action: str, meeting_id: Optional[str] = None):
    """Main slash command handler."""
    
    if action == "new":
        await handle_new_meeting(interaction)
    elif action == "update":
        if not meeting_id:
            await interaction.response.send_message("❌ Meeting ID is required for update command.", ephemeral=True)
            return
        await handle_update_meeting(interaction, meeting_id)
    elif action == "close":
        if not meeting_id:
            await interaction.response.send_message("❌ Meeting ID is required for close command.", ephemeral=True)
            return
        await handle_close_meeting(interaction, meeting_id)


async def handle_new_meeting(interaction: discord.Interaction):
    """Handle creating a new meeting."""
    try:
        modal = CreateMeetingModal()
        await interaction.response.send_modal(modal)

    except Exception as e:
        print(f"Error creating meeting: {e}")
        await interaction.response.send_message("❌ Failed to create meeting. Please try again.", ephemeral=True)


async def handle_update_meeting(interaction: discord.Interaction, meeting_id: str):
    """Handle updating a meeting with a modal form."""
    try:
        meeting = bot.storage.load_meeting(meeting_id)
        if not meeting:
            await interaction.response.send_message(f"❌ Meeting `{meeting_id}` not found.", ephemeral=True)
            return
        
        if meeting.is_closed:
            await interaction.response.send_message(f"❌ Meeting `{meeting_id}` is closed and cannot be updated.", ephemeral=True)
            return

        # Check if user has already submitted an update for this meeting
        user_str = str(interaction.user)
        if any(update.user == user_str for update in meeting.updates):
            await interaction.response.send_message(f"❌ You have already submitted an update for meeting `{meeting_id}`.", ephemeral=True)
            return
        
        modal = UpdateModal(meeting_id)
        await interaction.response.send_modal(modal)
        
    except Exception as e:
        print(f"Error handling update: {e}")
        await interaction.response.send_message("❌ Failed to process update request. Please try again.", ephemeral=True)


async def handle_close_meeting(interaction: discord.Interaction, meeting_id: str):
    """Handle closing a meeting."""
    try:
        meeting = bot.storage.load_meeting(meeting_id)
        if not meeting:
            await interaction.response.send_message(f"❌ Meeting `{meeting_id}` not found.", ephemeral=True)
            return
        
        if meeting.is_closed:
            await interaction.response.send_message(f"❌ Meeting `{meeting_id}` is already closed.", ephemeral=True)
            return
        
        if str(interaction.user) != meeting.created_by:
            await interaction.response.send_message(f"❌ You did not open this meeting.", ephemeral=True)
            return

        meeting.close()
        bot.storage.save_meeting(meeting)
        
        # Upload to S3 (silent operation)
        if bot.s3_storage and bot.s3_storage.is_available():
            try:
                # Generate HTML report
                html_content = bot.report_generator.generate_html_report(meeting)
                if html_content:
                    bot.s3_storage.upload_meeting_json(meeting_id, meeting.to_dict())
                    bot.s3_storage.upload_html_report(meeting_id, html_content)
                else:
                    print(f"Warning: Could not generate HTML report for meeting {meeting_id}")
                
                presigned_url = bot.s3_storage.generate_presigned_url(meeting_id)
            except Exception as e:
                print(f"Warning: S3 upload failed for meeting {meeting_id}: {e}")
                # Continue with Discord response even if S3 fails
        else:
            print(f"S3 not available, skipping upload for meeting {meeting_id}")
        
        presigned_url = presigned_url if presigned_url else "Automatic presigned url unavailable"
        
        # Generate summary
        embed = discord.Embed(
            title="🔒 Meeting Closed",
            description=f"Meeting `{meeting_id}` has been closed.",
            color=0xff6b6b
        )

        embed.add_field(name="Total Updates", value=str(len(meeting.updates)), inline=True)
        embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
        embed.add_field(name="Closed at", value=f"<t:{int(interaction.created_at.timestamp())}:F>", inline=True)

        embed.add_field(name="View meeting report at presigned url:", value=presigned_url, inline=False)
        
        link = meeting.link if meeting.link else "This meeting has no link."
        embed.add_field(name="Join meeting at link:", value=link, inline=False)
        
        embed.set_footer(text="Meeting data has been saved and locked.")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        print(f"Error closing meeting: {e}")
        await interaction.response.send_message("❌ Failed to close meeting. Please try again.", ephemeral=True)


class UpdateModal(discord.ui.Modal, title="Meeting Update"):
    """Modal form for submitting meeting updates."""
    
    def __init__(self, meeting_id: str):
        super().__init__()
        self.meeting_id = meeting_id
    
    progress = discord.ui.TextInput(
        label="Progress",
        placeholder="What have you accomplished since the last update?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    blockers = discord.ui.TextInput(
        label="Blockers",
        placeholder="What is blocking your progress?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    goals = discord.ui.TextInput(
        label="Goals",
        placeholder="What are your goals for the next period?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        try:
            meeting = bot.storage.load_meeting(self.meeting_id)
            meeting.add_update(
                user=str(interaction.user),
                progress=self.progress.value.strip(),
                blockers=self.blockers.value.strip(),
                goals=self.goals.value.strip()
            )
            
            bot.storage.save_meeting(meeting)
            
            embed = discord.Embed(
                title="✅ Update Added",
                description=f"Your update has been added to meeting `{self.meeting_id}`",
                color=0x00ff00
            )
            embed.add_field(name="Progress", value=self.progress.value[:1000], inline=False)
            embed.add_field(name="Blockers", value=self.blockers.value[:1000], inline=False)
            embed.add_field(name="Goals", value=self.goals.value[:1000], inline=False)
            embed.add_field(name="Total Updates", value=str(len(meeting.updates)), inline=True)
            embed.add_field(name="Updated by", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            await interaction.response.send_message(f"❌ Validation error: {str(e)}", ephemeral=True)
        except Exception as e:
            print(f"Error submitting update: {e}")
            await interaction.response.send_message("❌ Failed to submit update. Please try again.", ephemeral=True)

class CreateMeetingModal(discord.ui.Modal, title="Create Meeting"):
    """Modal form for creating a new meeting."""
    
    def __init__(self):
        super().__init__()
    
    name = discord.ui.TextInput(
        label="Name",
        placeholder="What is the name of the meeting?",
        style=discord.TextStyle.paragraph,
        max_length=50,
        required=False
    )
    
    link = discord.ui.TextInput(
        label="Link",
        placeholder="What is the link to the meeting?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        try:
            name = self.name.value.strip() if self.name.value else ""
            link = self.link.value.strip() if self.link.value else ""
            meeting = Meeting.create_new(created_by=str(interaction.user), name=name, link=link)
            bot.storage.save_meeting(meeting)
            
            embed = discord.Embed(
                title="✅ New Meeting Created",
                description=f"Meeting ID: `{meeting.id}`",
                color=0x00ff00
            )
            embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Created at", value=f"<t:{int(interaction.created_at.timestamp())}:F>", inline=True)
            embed.add_field(name="Updates", value="0", inline=True)
            
            embed.set_footer(text="Use /meetingbot update <meeting_id> to add updates")
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error creating meeting: {e}")
            await interaction.response.send_message("❌ Failed to create meeting. Please try again.", ephemeral=True)

def main():
    """Main function to run the bot."""
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord bot token.")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord bot token!")
    except Exception as e:
        print(f"❌ Error running bot: {e}")


if __name__ == "__main__":
    main()

