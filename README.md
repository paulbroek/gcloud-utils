# gcloud-utils
Google Cloud utilities, my tips, tricks and helper functions to interact with BigQuery, Storage and more

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