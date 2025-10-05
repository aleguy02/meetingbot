# 🛠️ High-Level Architecture (Revised)

1. **Discord Bot (Python)**

   * Commands:

     * `/meetingbot new` → generates a unique `meeting_id`.
     * `/meetingbot update <meeting_id>` → sends an interactive modal form (Discord supports slash command options & modals).
     * `/meetingbot close <meeting_id>` → compiles data, generates HTML + spreadsheet, uploads to S3, and returns link.

2. **Data Handling**

   * Store meeting state in memory or in a json file at ./json/meetingid/meeting.json during development.
   * Later add persistence:

     * DynamoDB (scalable).
     * Or even just JSON blobs in S3 (cheap and simple).
     Don't worry about this too much now, just focus on rapid development

3. **Artifact Generation**

   * **Spreadsheet (CSV/Excel)**: generate a csv file for each update and its properties
   * **HTML Report**: generate templated HTML (with Jinja).
   * Files generated locally → then uploaded to S3.

4. **S3 Usage**

   * Store meeting artifacts under paths like:

     ```
     s3://mybucket/meetings/<meeting_id>/index.html
     s3://mybucket/meetings/<meeting_id>/meeting.xlsx
     ```
   * **S3 Static Website Hosting** will be enabled
   * Bot responds with link:

     ```
     https://mydomain.com/meetingbot/<meeting_id>/
     ```

---

# 📋 Step-by-Step Instructions (DEPRECATED)
## IMPORTANT: This section is DEPRECATED, it is only here if you want to take inspiration from this but is by no means required.
### Step 1: Set up the Discord Bot in Go

* Install `discordgo`:

  ```bash
  go get github.com/bwmarrin/discordgo
  ```
* Create a bot in [Discord Developer Portal](https://discord.com/developers/applications).
* Add bot token to environment variables (`DISCORD_TOKEN`).
* In your Go app:

  * Register slash commands (`/meetingbot new`, `/meetingbot update`, `/meetingbot close`).
  * Use `discordgo.InteractionCreate` to handle them.

---

### Step 2: Define Meeting Data Models

Example Go struct:

```go
type Update struct {
    User     string
    Progress string
    Blockers string
    Goals    string
}

type Meeting struct {
    ID      string
    Updates []Update
}
```

* Keep an in-memory `map[string]*Meeting` for active meetings.
* Later: persist JSON blobs in S3 (`meetings/<id>/data.json`).

---

### Step 3: Collect Updates via Modals

* Use `discordgo.InteractionResponseModal` for a nice form:

  * Fields: Progress, Blockers, Goals.
* On submit → parse data → append to the `Meeting.Updates`.

---

### Step 4: Generate Artifacts

**CSV/Excel**


Sample `templates/meeting.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Meeting {{.ID}}</title>
</head>
<body>
  <h1>Meeting {{.ID}}</h1>
  {{range .Updates}}
    <div>
      <h2>{{.User}}</h2>
      <p><b>Progress:</b> {{.Progress}}</p>
      <p><b>Blockers:</b> {{.Blockers}}</p>
      <p><b>Goals:</b> {{.Goals}}</p>
    </div>
  {{end}}
</body>
</html>
```

---

### Step 5: Upload to S3

* Use AWS SDK for Python to upload to S3

---

### Step 6: Closing a Meeting

When `/meetingbot close <id>` is called:

1. Gather meeting data.
2. Generate HTML + CSV.
3. Upload both to S3.
4. Respond in Discord:

   ```
   Your meeting summary: https://mydomain.com/meetingbot/<id>/
   ```

