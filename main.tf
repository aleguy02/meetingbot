provider "aws" {
  region = var.region
}

data "aws_ami" "amzn_linux_2023" {
  most_recent = true

  filter {
    name   = "name"
    values = ["al2023-ami-2023.9.20251014.0-kernel-6.1-x86_64"]
  }

  owners = ["137112412989"]
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.amzn_linux_2023.id
  instance_type          = "t3.micro"
  key_name               = var.instance_key_name
  vpc_security_group_ids = [aws_security_group.ssh.id]
  user_data              = templatefile("${path.module}/deploy.sh", {
    DISCORD_TOKEN         = var.discord_token
    DISCORD_GUILD_IDS     = var.discord_guild_ids
    AWS_ACCESS_KEY_ID     = var.aws_access_key_id
    AWS_SECRET_ACCESS_KEY = var.aws_secret_access_key
    AWS_S3_BUCKET         = aws_s3_bucket.app_bucket.id
  })

  tags = {
    Name = var.instance_name
  }
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "ssh" {
  name        = "allow_ssh"
  description = "Allow SSH inbound"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_ssh"
  }
}

resource "aws_s3_bucket" "app_bucket" {
  bucket_prefix = "meetingbot-s3-dev-"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_bucket" {
  bucket = aws_s3_bucket.app_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

    bucket_key_enabled = false
  }
}

resource "aws_s3_bucket_public_access_block" "app_bucket" {
  bucket = aws_s3_bucket.app_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}
