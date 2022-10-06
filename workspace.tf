# Dependent resources for Azure Machine Learning

resource "azurerm_application_insights" "terra" {
  name                = "appinsight"
  location            = azurerm_resource_group.terra.location
  resource_group_name = azurerm_resource_group.terra.name
  application_type    = "web"
}


resource "azurerm_container_registry" "terra" {
  name                = "testfordays"
  location            = azurerm_resource_group.terra.location
  resource_group_name = azurerm_resource_group.terra.name
  sku                 = "Premium"
  admin_enabled       = true
}

resource "azurerm_key_vault" "terra" {
  name                     = "testfordays"
  location                 = azurerm_resource_group.terra.location
  resource_group_name      = azurerm_resource_group.terra.name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "premium"
  purge_protection_enabled = false
}

# Machine Learning workspace
resource "azurerm_machine_learning_workspace" "terra" {
  name                    = "my_ws"
  location                = azurerm_resource_group.terra.location
  resource_group_name     = azurerm_resource_group.terra.name
  application_insights_id = azurerm_application_insights.terra.id
  key_vault_id            = azurerm_key_vault.terra.id
  storage_account_id      = azurerm_storage_account.terra.id
  container_registry_id   = azurerm_container_registry.terra.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "terra" {
  name                     = "testfordays"
  location                 = azurerm_resource_group.terra.location
  resource_group_name      = azurerm_resource_group.terra.name
  account_tier             = "Standard"
  account_replication_type = "GRS"
}



