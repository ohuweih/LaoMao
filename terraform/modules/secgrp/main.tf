resource "aws_security_group" "terraform_secgrp" {
    name = "terraform_secgrp"
    description = "Allow ssh and http traffic from my personal computer"
    vpc_id = var.vpc_id

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["207.174.253.122/32", "10.0.0.0/8"]
    }

    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["207.174.253.122/32", "10.0.0.0/8"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "terraform_secgrp"
        ManagedBy = "terraform"
    }
}
