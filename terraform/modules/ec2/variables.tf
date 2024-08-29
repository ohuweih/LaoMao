variable "ami_id" {
    description = "ami to create ec2"
    type = string
}


variable "instance_type" {
    description = "type of ec2"
    type = string
}


variable "subnet_ids" {
    description = "subnet ec2 lives in"
    type = list(string)
}


variable "secgrp" {
    description = "secgrp to attach tp ec2"
    type = string
}


variable "key_name" {
    description = "key to attach to ec2"
    type = string
}

variable "number_of_instances" {
    description = "Number of instances to be created"
    type = number
    default = 1
}
