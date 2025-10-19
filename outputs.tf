output "bucket_name" {
  description = "The name of the created S3 bucket"
  value       = aws_s3_bucket.app_bucket.id
}

output "instance_public_dns" {
  description = "The public DNS of the created instance"
  value       = aws_instance.app_server.public_dns
}