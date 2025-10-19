variable "instance_name" {
  description = "Value of the EC2 instance's Name tag"
  type        = string
  default     = "meetingbot-ec2-dev"
}

variable "instance_key_name" {
  description = "The name of the AWS key pair to access the EC2 instance"
  type        = string
  default     = "aws-ec2-key-pair"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

## Environment variables
variable "discord_token" {
  description = "Your Discord application's Bot token"
  type      = string
  sensitive = true
}

variable "discord_guild_ids" {
  description = "A comma separated list of the IDs of the servers to which you want to deploy the bot"
  type = string
}

variable "aws_access_key_id" {
  type      = string
  sensitive = true
}

variable "aws_secret_access_key" {
  type      = string
  sensitive = true
}