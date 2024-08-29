terraform {
  source = "../../../modules/igw"
}

dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
    vpc_id = dependency.vpc.outputs.terraform_vpc_id
} 
