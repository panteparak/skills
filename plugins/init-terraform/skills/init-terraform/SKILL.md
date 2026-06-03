---
name: init-terraform
description: Scaffold Terraform infrastructure-as-code projects with proper module structure, state management, and environment separation. Use when creating or organizing Terraform IaC.
argument-hint: "[project-name] [cloud-provider]"
disable-model-invocation: true
---

# Initialize Terraform Project

Scaffold a production-grade Terraform project for: **$ARGUMENTS**

Default cloud provider: AWS if not specified.

## Step 1: Project Structure

```
$0/
├── environments/                      # Per-environment configs
│   ├── dev/
│   │   ├── main.tf                    # Module calls with dev values
│   │   ├── variables.tf
│   │   ├── terraform.tfvars           # Dev-specific variable values
│   │   ├── backend.tf                 # S3 backend for dev state
│   │   └── providers.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── providers.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       ├── backend.tf
│       └── providers.tf
│
├── modules/                           # Reusable modules
│   ├── networking/
│   │   ├── main.tf                    # VPC, subnets, NAT, IGW
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── database/
│   │   ├── main.tf                    # RDS/Aurora
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── compute/
│   │   ├── main.tf                    # ECS/EKS/EC2
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── monitoring/
│       ├── main.tf                    # CloudWatch, alarms
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
│
├── .terraform-version                 # Pin Terraform version
├── .tflint.hcl                        # TFLint config
├── Makefile
└── README.md
```

## Step 2: Remote State Backend

### backend.tf (per environment)
```hcl
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "$0/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Bootstrap state bucket (one-time)
```hcl
# bootstrap/main.tf — run once to create state infrastructure
resource "aws_s3_bucket" "terraform_state" {
  bucket = "company-terraform-state"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

## Step 3: Module Design Pattern

### modules/networking/main.tf
```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-vpc"
  })
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-public-${count.index}"
    Type = "public"
  })
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-private-${count.index}"
    Type = "private"
  })
}
```

### modules/networking/variables.tf
```hcl
variable "project" {
  type        = string
  description = "Project name for resource naming"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
}

variable "tags" {
  type        = map(string)
  description = "Common tags for all resources"
  default     = {}
}
```

### modules/networking/outputs.tf
```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the VPC"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "IDs of public subnets"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "IDs of private subnets"
}
```

## Step 4: Environment Configuration

### environments/dev/main.tf
```hcl
module "networking" {
  source = "../../modules/networking"

  project             = var.project
  environment         = "dev"
  vpc_cidr            = "10.0.0.0/16"
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]
  availability_zones  = ["us-east-1a", "us-east-1b"]
  tags                = local.common_tags
}

module "database" {
  source = "../../modules/database"

  project        = var.project
  environment    = "dev"
  vpc_id         = module.networking.vpc_id
  subnet_ids     = module.networking.private_subnet_ids
  instance_class = "db.t3.small"       # Smaller for dev
  tags           = local.common_tags
}

locals {
  common_tags = {
    Project     = var.project
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
```

## Step 5: Tooling

### Makefile
```makefile
ENV ?= dev

init:
	cd environments/$(ENV) && terraform init

plan:
	cd environments/$(ENV) && terraform plan

apply:
	cd environments/$(ENV) && terraform apply

destroy:
	cd environments/$(ENV) && terraform destroy

fmt:
	terraform fmt -recursive

validate:
	cd environments/$(ENV) && terraform validate

lint:
	tflint --recursive
```

### .tflint.hcl
```hcl
plugin "aws" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "terraform_naming_convention" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}
```

## Rules
- **Remote state** — always use remote backend with locking (S3+DynamoDB, GCS, etc.)
- **State per environment** — never share state between dev/staging/prod
- **Pin versions** — pin Terraform version, provider versions, module versions
- **Variables have descriptions** — every variable documented
- **Outputs have descriptions** — every output documented
- **Modules are reusable** — no hardcoded values, parameterize everything
- **Tags on everything** — project, environment, managed-by at minimum
- **No secrets in tfvars** — use AWS Secrets Manager, Vault, or env vars
- **`prevent_destroy`** on critical resources (state bucket, production DB)
- **Run `terraform fmt`** before every commit
- **Plan before apply** — always review the plan
