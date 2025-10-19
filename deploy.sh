#!/bin/bash
set -e

cat > /etc/meetingbot.env <<'EOF'
DISCORD_TOKEN=${DISCORD_TOKEN}
DISCORD_GUILD_IDS=${DISCORD_GUILD_IDS}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_S3_BUCKET=${AWS_S3_BUCKET}
EOF

exec > >(tee /var/log/deploy.log) 2>&1


echo "=== Updating and installing packages ==="
dnf update -y
dnf install -y git docker
echo


echo "=== Starting docker service ==="
service docker start
usermod -a -G docker ec2-user
echo


echo "=== Deploying meetingbot ==="
git clone https://github.com/aleguy02/meetingbot.git /opt/meetingbot
docker build -t meetingbot:latest /opt/meetingbot/
docker run -d --name meetingbot \
--env-file /etc/meetingbot.env \
-v /opt/meetingbot/json:/meetingbot/json \
meetingbot:latest