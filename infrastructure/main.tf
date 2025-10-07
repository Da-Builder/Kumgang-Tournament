provider "aws" {
  region = var.region

  default_tags { tags = {
    Project = var.project
  } }
}


resource "aws_iam_role" "role" {
  name = lower("${var.project}-role")
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = {
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
  } })
}


resource "aws_iam_role_policy_attachment" "policy" {
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess_v2"
}


resource "aws_dynamodb_table" "database" {
  name = lower("${var.project}-database")

  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20

  hash_key = "name"
  attribute {
    name = "name"
    type = "S"
  }

  provisioner "local-exec" {
    command = "python ../script/database.py ${self.name}"
  }
}


resource "aws_ecr_repository" "registry" {
  name         = lower("${var.project}-registry")
  force_delete = true

  provisioner "local-exec" {
    command = <<-EO
      podman build --tag=${self.repository_url} ..
      aws --region=${var.region} ecr get-login-password | podman login --username=AWS --password-stdin ${self.repository_url}
      podman push ${self.repository_url}
    EO
  }
}


resource "aws_lambda_function" "server" {
  function_name = lower("${var.project}-server")
  role          = aws_iam_role.role.arn
  timeout       = 5

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.registry.repository_url}:latest"

  environment { variables = {
    PASSHASH = sha256(var.password)
    DATABASE = aws_dynamodb_table.database.name
  } }
}


resource "aws_lambda_function_url" "endpoint" {
  function_name      = aws_lambda_function.server.function_name
  authorization_type = "NONE"
}
