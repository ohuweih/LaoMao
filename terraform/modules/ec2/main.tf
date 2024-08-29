resource "random_integer" "random_subnet_index" {
    count = var.number_of_instances
    min = 0
    max = length(var.subnet_ids) - 1
}

locals {
    random_subnet_id = [for i in random_integer.random_subnet_index : element(var.subnet_ids, i.result)]
}


resource "aws_instance" "terraform_apache_instance" {
    count = var.number_of_instances
    ami = var.ami_id
    instance_type = var.instance_type
    subnet_id = local.random_subnet_id[count.index]
    key_name = var.key_name
    vpc_security_group_ids = [var.secgrp]

    user_data = <<-EOF
                #!/bin/bash
                sudo dnf install httpd -y
                echo '${(base64encode(templatefile("${path.module}/files/index.html", {})))}' | base64 -d 2&> /var/www/html/index.html
                systemctl enable httpd
                systemctl start httpd
                EOF

    tags = {
        Name = "terraform_apache_instance_${count.index + 1}"
        ManagedBy = "terraform"
        SubnetId = local.random_subnet_id[count.index]
    }
}
