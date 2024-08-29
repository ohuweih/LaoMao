terraform {
  source = "../../../modules/routeTable"
}


dependency "vpc" {
  config_path = "../vpc"
}


dependency "igw" {
  config_path = "../igw"
}


inputs = {
  vpc_id = dependency.vpc.outputs.terraform_vpc_id
  igw_id = dependency.igw.outputs.terraform_igw_id
  rt_cidr = "0.0.0.0/0"      # Using the output from the VPC module
}
