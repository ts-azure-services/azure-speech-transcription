#!/bin/bash
#Script to provision Cognitive Services account
grn=$'\e[1;32m'
end=$'\e[0m'

# Start of script
SECONDS=0
printf "${grn}STARTING CREATION OF SPEECH SERVICE...${end}\n"

# Source subscription ID, and prep config file
source sub.env
sub_id=$SUB_ID
email_id=$EMAIL_ID

# Set the default subscription 
az account set -s $sub_id

# Create the resource group, location
number=$[ ( $RANDOM % 10000 ) + 1 ]
resourcegroup='cs'$number
speechservice='cs'$number'speech'
storageaccount='cs'$number'storageaccount'
blobcontainer='cs'$number'container'
location='westus2'
end_date=$(date -j -v +2d +"%Y-%m-%d")
blob_file_directory='audio-files'

printf "${grn}starting creation of resource group...${end}\n"
rgCreate=$(az group create --name $resourcegroup --location $location)
printf "Result of resource group create:\n $rgCreate \n"

## Create speech service
printf "${grn}creating the speech service...${end}\n"
speechServiceCreate=$(az cognitiveservices account create \
	--name $speechservice \
	-g $resourcegroup \
	--kind 'SpeechServices' \
	--sku S0 \
	--location $location \
	--yes)
printf "Result of speech service create:\n $speechServiceCreate \n"

## Retrieve key from cognitive services
printf "${grn}retrieve keys & endpoints for speech service...${end}\n"
speechKey=$(az cognitiveservices account keys list -g $resourcegroup --name $speechservice --query "key1" -o tsv)
speechEndpoint=$(az cognitiveservices account show -g $resourcegroup --n $speechservice --query "properties.endpoint" -o tsv)

# Create the storage account
printf "${grn}starting creation of the storage account...${end}\n"
storageAcctCreate=$(az storage account create \
	--name $storageaccount \
	-g $resourcegroup \
	-l $location \
	--kind StorageV2 \
	--sku Standard_LRS)
printf "Result of storage account create:\n $storageAcctCreate \n"

# Create the blob container
conn_string=$(az storage account show-connection-string --name $storageaccount -g $resourcegroup --query "connectionString")

printf "${grn}starting creation of the blob container...${end}\n"
blobContainerCreate=$(az storage container create --connection-string $conn_string --name $blobcontainer)
printf "Result of first blob container create:\n $blobContainerCreate \n"

# Retrieve object id of user email
user_object_id=$(az ad user list --filter "mail eq '$email_id'" --query "[].id" -o tsv)

printf "${grn}assigning storage blob data contributor to storage account...${end}\n"
contributorRole=$(az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee $user_object_id \
    --scope "/subscriptions/$sub_id/resourceGroups/$resourcegroup/providers/Microsoft.Storage/storageAccounts/$storageaccount")
printf "Result of storage blob data contributor:\n $contributorRole \n"
sleep 10

printf "${grn}generate sas token for blob container...${end}\n"
firstsastoken=$(az storage container generate-sas \
	--account-name $storageaccount --name $blobcontainer --https-only \
	--as-user --auth-mode login \
	--permissions dlrw \
	--expiry $end_date
)
	#--connection-string $conn_string)
#printf "Result of first container SAS token:\n $firstsastoken \n"
#echo $firstsastoken
first_sas_token=$(sed -e 's/^"//' -e 's/"$//' <<<"$firstsastoken")
firstsasurl=https://$storageaccount.blob.core.windows.net/$blobcontainer?$first_sas_token

# Upload the blob storage
printf "${grn}uploading the raw data...${end}\n"
az storage blob directory upload --connection-string $conn_string \
	-c $blobcontainer -s './data-feeds/wav-files/*' -d $blob_file_directory --recursive

# Create environment file 
printf "${grn}WRITING OUT ENVIRONMENT VARIABLES...${end}\n"
configFile='variables.env'
printf "RESOURCE_GROUP=$resourcegroup \n"> $configFile
printf "SPEECH_KEY=$speechKey \n">> $configFile
printf "SPEECH_LOCATION=$location \n">> $configFile
printf "SPEECH_ENDPOINT=$speechEndpoint \n">> $configFile
printf "STORAGE_ACCOUNT=$storageaccount \n">> $configFile
printf "STORAGE_CONN_STRING=$conn_string \n">> $configFile
printf "BLOB_CONTAINER_NAME=$blobcontainer \n">> $configFile
echo "BLOB_CONTAINER_SAS_TOKEN=$first_sas_token">> $configFile
echo "BLOB_CONTAINER_SAS_URL=$firstsasurl">> $configFile
