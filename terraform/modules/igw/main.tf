### add internet gatway ###
resource "aws_internet_gateway" "terraform_igw" {
    vpc_id = var.vpc_id

    tags = {
        Name = "terraform_igw"
        ManagedBy = "terraform"
    }
}
