terraform {
    source = "../../../modules/subnet"
}

dependency "vpc" {
    config_path = "../vpc"
}

inputs = {
    subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24", "10.0.5.0/25"]
    availability_zone = ["us-east-2a", "us-east-2b", "us-east-2c"]
    vpc_id = dependency.vpc.outputs.terraform_vpc_id
}
