terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.76.0"
    }
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

# Provides the Resource Group to contain ressources
resource "azurerm_resource_group" "terra" {
  name     = "my_terra_rg"
  location = "Germany West Central"
  tags = {
    environment = "dev"
    source      = "Terraform"
  }
}