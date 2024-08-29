### add subnet ###
resource "aws_subnet" "terraform_subnet" {
    count = length(var.subnet_cidrs)

    vpc_id = var.vpc_id
    cidr_block = var.subnet_cidrs[count.index]
    availability_zone = element(var.availability_zones, count.index % length(var.availability_zones))
    map_public_ip_on_launch = true

    tags = {
        Name = "terraform_subnet_${count.index + 1}"
        ManagedBy = "terraform"
        AvailabilityZone = element(var.availability_zones, count.index % length(var.availability_zones))
        CidrBlock = var.subnet_cidrs[count.index]
        AutoAssignIP = "True"
    }
}
