variable "subnet_ids" {
    description = "list of subnet IDs"
    type = list(string)
}


variable "rt_id" {
    description = "ID for our route table"
    type = string
}
