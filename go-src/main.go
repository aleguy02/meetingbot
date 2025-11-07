package main

import (
	"errors"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

// Bot wraps a Discord session and command handlers
type Bot struct {
	session         *discordgo.Session
	commands        []*discordgo.ApplicationCommand
	commandHandlers map[string]func(s *discordgo.Session, i *discordgo.InteractionCreate)
}

func NewBot(token string) (*Bot, error) {
	s, err := discordgo.New("Bot " + token)
	if err != nil {
		return nil, fmt.Errorf("invalid bot parameters: %v", err)
	}

	bot := &Bot{
		session: s,
		commands: []*discordgo.ApplicationCommand{
			{
				Name:        "meetingbot",
				Description: "Meeting management commands",
				Options: []*discordgo.ApplicationCommandOption{
					{
						Name:        "new",
						Description: "Initialize a new meeting",
						Type:        discordgo.ApplicationCommandOptionSubCommand,
					},
					{
						Name:        "update",
						Description: "Update an existing meeting",
						Type:        discordgo.ApplicationCommandOptionSubCommand,
					},
					{
						Name:        "close",
						Description: "Close a meeting",
						Type:        discordgo.ApplicationCommandOptionSubCommand,
					},
				},
			},
		},
		commandHandlers: map[string]func(s *discordgo.Session, i *discordgo.InteractionCreate){
			"meetingbot": func(s *discordgo.Session, i *discordgo.InteractionCreate) {
				subcommand := i.ApplicationCommandData().Options[0].Name

				switch subcommand {
				case "new":
					err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseModal,
						Data: &discordgo.InteractionResponseData{
							CustomID: "new_meeting_" + i.Interaction.Member.User.ID,
							Title: "Create Meeting",
							Components: []discordgo.MessageComponent{
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										discordgo.TextInput{
											CustomID:    "meeting_name",
											Label:       "Name",
											Placeholder: "What is the name of the meeting?",
											Style:       discordgo.TextInputParagraph,
											Required:    true,
											MaxLength:   50,
										},
									},
								},
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										discordgo.TextInput{
											CustomID:    "meeting_link",
											Label:       "Link",
											Placeholder: "What is the link to the meeting?",
											Style:       discordgo.TextInputParagraph,
											Required:    false,
											MaxLength:   500,
										},
									},
								},
							},
						},
					})
					if err != nil {
						panic(err)
					}
				case "update":
					err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseModal,
						Data: &discordgo.InteractionResponseData{
							CustomID: "meeting_update_" + i.Interaction.Member.User.ID,
							Title: "Meeting Update",
							Components: []discordgo.MessageComponent{
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										discordgo.TextInput{
											CustomID:    "progress",
											Label:       "Progress",
											Placeholder: "What have you accomplished since the last update?",
											Style:       discordgo.TextInputParagraph,
											Required:    true,
											MaxLength:   500,
										},
									},
								},
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										discordgo.TextInput{
											CustomID:    "blockers",
											Label:       "Blockers",
											Placeholder: "What is blocking your progress?",
											Style:       discordgo.TextInputParagraph,
											Required:    true,
											MaxLength:   500,
										},
									},
								},
								discordgo.ActionsRow{
									Components: []discordgo.MessageComponent{
										discordgo.TextInput{
											CustomID:    "goals",
											Label:       "Goals",
											Placeholder: "What are your goals for the next period?",
											Style:       discordgo.TextInputParagraph,
											Required:    true,
											MaxLength:   500,
										},
									},
								},
							},
						},
					})
					if err != nil {
						panic(err)
					}
				case "close":
					s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseChannelMessageWithSource,
						Data: &discordgo.InteractionResponseData{
							Content: "Hello from /meeting close",
						},
					})
				}

			},
		},
	}

	s.AddHandler(bot.interactionCreate)

	return bot, nil
}

// interactionCreate handles slash command interactions
func (b *Bot) interactionCreate(s *discordgo.Session, i *discordgo.InteractionCreate) {
	log.Println("interactionCreate")
	switch i.Type {
	case discordgo.InteractionApplicationCommand:
		if handler, ok := b.commandHandlers[i.ApplicationCommandData().Name]; ok {
			handler(s, i)
		}
	case discordgo.InteractionModalSubmit:
		err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: "Thank you for taking your time to fill this survey",
				Flags:   discordgo.MessageFlagsEphemeral,
			},
		})
		if err != nil {
			panic(err)
		}
		i.ModalSubmitData()
	}
}

func (b *Bot) SyncCommands() error {
	appID := os.Getenv("APPLICATION_ID")
	if appID == "" {
		return errors.New("❌ APPLICATION_ID not found in environment variables! Please create a .env file with your Discord application ID")
	}

	guildIDsEnv := os.Getenv("DISCORD_GUILD_IDS")
	guildIDs := []string{}

	if guildIDsEnv != "" {
		for _, g := range strings.Split(guildIDsEnv, ",") {
			guildIDs = append(guildIDs, g)
		}
	}

	if len(guildIDs) > 0 {
		// Per-guild sync for instant availability in each server
		for _, g := range guildIDs {
			for _, cmd := range b.commands {
				_, err := b.session.ApplicationCommandCreate(appID, g, cmd)
				if err != nil {
					return fmt.Errorf("failed to create command %q: %w", cmd.Name, err)
				}
			}
		}
		log.Printf("Synced slash commands for guilds: %v\n", guildIDs)
	} else {
		// Global sync (may take up to ~1 hour to propagate)
		return errors.New("global sync not supported. Please create DISCORD_GUILD_IDs in your .env file")
		// fmt.Println("Synced global slash commands")
	}

	return nil
}

func (b *Bot) Open() error {
	return b.session.Open()
}

func (b *Bot) Close() error {
	return b.session.Close()
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("error loading .env file")
	}

	token := os.Getenv("DISCORD_TOKEN")
	if token == "" {
		log.Fatal("❌ DISCORD_TOKEN not found in environment variables! Please create a .env file with your Discord bot token")
	}

	bot, err := NewBot(token)
	if err != nil {
		log.Fatalf("Failed to create bot: %v", err)
	}

	err = bot.SyncCommands()
	if err != nil {
		log.Fatalf("Failed to sync commands: %v", err)
	}

	err = bot.Open()
	if err != nil {
		log.Fatalf("Failed to open connection: %v", err)
	}
	defer bot.Close()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt)
	log.Println("Press Ctrl+C to exit")
	<-stop
}
