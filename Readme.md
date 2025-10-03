# Kumgang Tournament
Scoreboard for [Kumgang Taekwondo](https://www.kumgang.co.nz/) tournament.



## Deployment
### Prerequisite
Ensure the following tools are installed:
- [AWS CLI](https://aws.amazon.com)
- [Terraform](https://developer.hashicorp.com/terraform)
- [Podman](https://podman.io) / Other OCI Container Engine (Required to build & push image on deployment)
- [Python](https://www.python.org) (Required to populate database on deployment)


### Instruction
From `/infrastructure` directory:
```Shell
terraform init
terraform apply
```
**Note:** Check `/infrastructure/variable.tf` for all available deployment variables.

Once deployment completes, the *Lambda Function URL* will be outputted.



## Technology
<div align="center"><img src="https://skillicons.dev/icons?i=python,js,html,css,fastapi,bootstrap,aws,dynamodb,terraform,docker"/></div>
