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