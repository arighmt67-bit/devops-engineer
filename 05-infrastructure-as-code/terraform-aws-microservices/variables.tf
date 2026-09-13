variable "aws_region" {
  description = "AWS region for provisioning"
  type        = string
  default     = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name identifier"
  type        = string
  default     = "forum-devops"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "Subnet CIDR block"
  type        = string
  default     = "10.0.1.0/24"
}
