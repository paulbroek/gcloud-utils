# gcloud-utils

Google Cloud utility function, to interact with BigQuery, Storage and more

## 1 Configure gcloud service-account

From Google Cloud [docs](https://cloud.google.com/docs/authentication/getting-started#command-line)

List service accounts

```bash
gcloud iam service-accounts list
```

Create service account

```bash
gcloud iam service-accounts create paulbroek
```

Grant permissions to the service account. Replace `PROJECT_ID` with your project ID

```bash
gcloud projects add-iam-policy-binding PROJECT_ID --member="serviceAccount:NAME@PROJECT_ID.iam.gserviceaccount.com" --role="roles/owner"
# e.g.
gcloud projects add-iam-policy-binding ob-train --member="serviceAccount:paulbroek@ob-train.iam.gserviceaccount.com" --role="roles/owner"
```

Generate the key file. Replace `FILE_NAME` with a name for the key file

```bash
gcloud iam service-accounts keys create FILE_NAME.json --iam-account=NAME@PROJECT_ID.iam.gserviceaccount.com
# e.g.
gcloud iam service-accounts keys create /home/paul/Downloads/service-account-file.json --iam-account=paulbroek@ob-train.iam.gserviceaccount.com
```

Setting the environment variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/home/paul/Downloads/service-account-file.json"
```

## 2 How to run

### 2.1 Build docker image to run monitor_billing as container

```bash
docker build -f ~/repos/gcloud-utils/Dockerfile -t gcloud_env  .
```

### 2.2 Copy gcloud credentials

```bash
vim ~/Downloads/service-account-file.json
# copy credentials from home pc into this file
```

### 2.3 Copy configuration files

```bash
# .env
CONFIG_FILE=/home/paul/repos/gcloud-utils/gcloud_utils/config

# config/config.yaml
# see below
```

`config.yaml`:

```yaml
# config.yaml
slack:
    api_key: MY_SLACK_API_KEY

bigquery:
    billing_table_name: MY_BILLING_TABLE_NAME
```

### 2.4 Run container

```bash
docker-compose up -d
```

### 2.5 Run locally

```bash
pip install -U ~/repos/gcloud-utils

export GCLOUD_CONFIG_FILE=/home/paul/repos/gcloud-utils/gcloud_utils/config/config.yaml && \
export GOOGLE_APPLICATION_CREDENTIALS="/home/paul/Downloads/service-account-file.json" && \
ipy -m gcloud_utils.monitor_billing -i -- --usd_threshold 0 --seconds 5 -v info
```
