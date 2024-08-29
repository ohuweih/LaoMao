output "terraform_subnets" {
  value = aws_subnet.terraform_subnet[*].id
}

output "terraform_cidrs" {
  value = aws_subnet.terraform_subnet[*].cidr_block
}
