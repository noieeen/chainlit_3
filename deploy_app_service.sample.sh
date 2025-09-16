    #!/bin/bash

    # Load environment variables from .env if it exists
if [ -f .env ]; then
  source .env
fi

SUBSCRIPTION="Azure subscription 1"
RESOURCEGROUP="DefaultResourceGroup-SEA"
LOCATION="southeastasia"
PLANNAME="ASP-DefaultResourceGroupSEA-a573"
PLANSKU="F1"
SITENAME="Chainlit"
RUNTIME="PYTHON|3.13"

# login supports device login, username/password, and service principals
# see https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest#az_login
az login
# list all of the available subscriptions
az account list -o table
# set the default subscription for subsequent operations
az account set --subscription $SUBSCRIPTION
# # create a resource group for your application
# az group create --name $RESOURCEGROUP --location $LOCATION
# # create an appservice plan (a machine) where your site will run
# az appservice plan create --name $PLANNAME --location $LOCATION --is-linux --sku $PLANSKU --resource-group $RESOURCEGROUP
# # create the web application on the plan
# # specify the node version your app requires
# az webapp create --name $SITENAME --plan $PLANNAME --runtime $RUNTIME --resource-group $RESOURCEGROUP


# Startup command: run Chainlit, bind to 0.0.0.0:8000
az webapp config set -g $RESOURCEGROUP -n $SITENAME \
  --startup-file "python -m chainlit run app.py --host 0.0.0.0 --port 8000"

# Turn on WebSockets (required for live UI updates)
az webapp config set -g $RESOURCEGROUP -n $SITENAME --web-sockets-enabled true

# Example: DB URL + build during deploy
az webapp config appsettings set -g $RESOURCEGROUP -n $SITENAME --settings \
  DATABASE_URL="$DATABASE_URL" \
  CHAINLIT_AUTH_SECRET="$CHAINLIT_AUTH_SECRET"  \
  BUCKET_NAME="$BUCKET_NAME" \
  DEV_AWS_ENDPOINT="$DEV_AWS_ENDPOINT" \
  APP_AWS_REGION="$APP_AWS_REGION" \
  APP_AWS_ACCESS_KEY="$APP_AWS_ACCESS_KEY" \
  APP_AWS_SECRET_KEY="$APP_AWS_SECRET_KEY" \
  SUPABASE_URL="$SUPABASE_URL" \
  SCM_DO_BUILD_DURING_DEPLOYMENT=true


az webapp up --name $SITENAME --resource-group $RESOURCEGROUP --runtime $RUNTIME --plan $PLANNAME --logs

# To set up deployment from a local git repository, uncomment the following commands.
# first, set the username and password (use environment variables!)
# USERNAME=""
# PASSWORD=""
# az webapp deployment user set --user-name $USERNAME --password $PASSWORD

# now, configure the site for deployment. in this case, we will deploy from the local git repository
# you can also configure your site to be deployed from a remote git repository or set up a CI/CD workflow
# az webapp deployment source config-local-git --name $SITENAME --resource-group $RESOURCEGROUP

# the previous command returned the git remote to deploy to
# use this to set up a new remote named "azure"
# git remote add azure "https://$USERNAME@$SITENAME.scm.azurewebsites.net/$SITENAME.git"
# push master to deploy the site
# git push azure master

# browse to the site
# az webapp browse --name $SITENAME --resource-group $RESOURCEGROUP
