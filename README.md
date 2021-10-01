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

## 2 Cuda and GPU usage

Sometimes you have to reinstall Cuda when using a new GPU type


### 2.1 Uninstall cuda from Ubuntu 

```bash
sudo apt-get -y purge nvidia*
sudo apt-get autoremove -y
sudo apt-get autoclean
sudo rm -rf /usr/local/cuda*
```

### 2.2 Install cuda

From Google Cloud [docs](https://cloud.google.com/compute/docs/gpus/install-drivers-gpu#ubuntu-driver-steps)

```bash
cd /tmp
curl -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt -y install cuda
```

### 2.3 Install cudnn

More [help](https://jayden-chua.medium.com/quick-install-cuda-on-google-cloud-compute-6c85447f86a1)

First get `cudnn-11.4-linux-x64-v8.2.4.15.tgz` file from nvidia, though user account.
Or copy from your ~/Downloads folder - through `gsutil` - to the VM
Then:
```bash
# unpack
cd ~/Downloads/
tar -xzvf cudnn-11.4-linux-x64-v8.2.4.15.tgz
```
Copy the following files into the CUDA Toolkit directory.
```bash
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include 
sudo cp -P cuda/lib64/libcudnn* /usr/local/cuda/lib64 
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```


## 3 docker

### 3.1 Build docker image to run monitor_billing as container

```bash
DOCKER_BUILDKIT=1 docker build -f ~/repos/gcloud-utils/Dockerfile -t gcloud_env --ssh github_ssh_key=/home/paul/.ssh/git_ssh_id_rsa .
```

### 3.2 Copy gcloud credentials



### 3.3 Run container

```bash
docker-compose up -d
```