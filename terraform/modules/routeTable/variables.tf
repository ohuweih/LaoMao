variable "vpc_id" {
    description = "the vpc id"
    type = string
}


variable "igw_id" {
    description = "the igw id"
    type = string
}


variable "rt_cidr" {
    description = "CIDR block for our route table"
    type = string
}
