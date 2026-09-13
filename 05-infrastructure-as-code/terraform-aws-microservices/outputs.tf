output "vpc_id" {
  description = "Provisioned VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Provisioned Public Subnet ID"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Provisioned Security Group ID"
  value       = aws_security_group.app_sg.id
}
