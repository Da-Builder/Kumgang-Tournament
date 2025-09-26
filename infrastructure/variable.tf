variable "region" {
  type        = string
  description = "The AWS region to deploy the infrastructure."
  default     = "ap-southeast-2" # Sydney Australia
}

variable "project" {
  type        = string
  description = "The project name. Used to prefix & tag infrastructure."
  default     = "Kumgang"
}


variable "password" {
  type        = string
  sensitive   = true
  description = "The password used for administrator access."

  validation {
    condition     = length(var.password) >= 8
    error_message = "Invalid Password: Must be >= 8 characters."
  }
}
