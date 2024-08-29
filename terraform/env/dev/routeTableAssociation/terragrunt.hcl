terraform {
  source = "../../../modules/routeTableAssociation"
}


dependency "subnet" {
  config_path = "../subnet"
}


dependency "routeTable" {
  config_path = "../routeTable"
}


inputs = {
  subnet_ids = dependency.subnet.outputs.terraform_subnets
  rt_id = dependency.routeTable.outputs.terraform_rt_id
}
