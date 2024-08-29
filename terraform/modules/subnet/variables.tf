variable "vpc_id" {
    description = "vpc id"
    type = string
}

variable "subnet_cidrs" {
    description = "CIDR blocks our subnets"
    type = list(string)
}


variable "availability_zones" {
  description = "List of available availability zones"
  type        = list(string)
  default     = ["us-east-2a", "us-east-2b", "us-east-2c"]
}
