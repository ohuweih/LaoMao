### add route table ###
resource "aws_route_table" "terraform_rt" {
    vpc_id = var.vpc_id

    route {
        cidr_block = var.rt_cidr
        gateway_id = var.igw_id
    }

    tags = {
        Name = "terraform_rt"
        ManagedBy = "terraform"
    }
}
