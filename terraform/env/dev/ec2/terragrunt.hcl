terraform {
  source = "../../../modules/ec2"
}

dependency "subnet" {
  config_path = "../subnet"
}

dependency "secgrp" {
  config_path = "../secgrp"
}

inputs = {
  number_of_instances = 9
  ami_id ="ami-0d77c9d87c7e619f9"
  instance_type = "t2.micro"
  subnet_ids = dependency.subnet.outputs.terraform_subnets
  secgrp = dependency.secgrp.outputs.terraform_secgrp_id
  key_name = "terraform_key"
}
