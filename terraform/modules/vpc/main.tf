### create vpc ###
resource "aws_vpc" "terraform_vpc" {
    cidr_block = var.vpc_cidr

    tags = {
        Name = "terraform_vpc"
        ManagedBy = "terraform"
    }
}
