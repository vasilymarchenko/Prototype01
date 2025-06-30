# Prototype01


# Azure preparations

```powershell
az group create --name prototype01-rg --location westeurope
```
This is needed for containerapp env creation. It's paid, disable later if not needed.
```powershell
az provider register -n Microsoft.OperationalInsights --wait
```
```powershell
az containerapp env create `
   --name prototype-env `
   --resource-group prototype01-rg `
   --location westeurope
```

# Pipeline secrets

1. `secrets.GHCR_TOKEN` - generate the token in GH with read/write permissions for packages
2. `secrets.AZURE_CREDENTIALS` get from the command:
``` powershell
az ad sp create-for-rbac --name "github-actions" --role contributor --scopes /subscriptions/{SubscriptionId}/resourceGroups/prototype01-rg --sdk-auth
```
Save the entire retrieved JSON as a GH secret