# Google cloud help and tips

## 1 General tips

See your own documentation file `howto.txt` in ubuntu/gcloud dir

### 1.1 Recommendations

If you need an 'expensive' machine like one with GPU / TPU, do the following

- Build your environment in a cheap compute instance. 4GB RAM intel costs only 3 cents / hour for instance
- Now when you're finished setting everything up (proper disk size, connect gdrive / storage buckets, run jupyter notebook succesfully), save the image in google cloud console
- Run an instance based on the image
- Do the heavy work, save results to gdrive / storage bucket
- Stop the instance, now it costs you 0 cents
- _All machine types are charged a minimum of 10 minutes. For example, if you run your virtual machine for 2 minutes, you will be billed for 10 minutes of usage._
- More pricing [info](https://blog.optimal.io/CPO200-Pricing-Questions-Google-Cloud/)
- Use Preemtipble VM instances (Google's name for spot instances), where possible. They come with discount but disappear after 24 hours, and can shutdown any time (though rarely)
	[info](https://cloud.google.com/compute/docs/instances/preemptible)
- 

### 1.2 SSH

It is not recommended not to manually add and remove SSH keys by editing project or instance metadata. 
Instead, use IAM roles to provide your public SSH key to the instance through your Google Account
Help:
https://cloud.google.com/compute/docs/instances/connecting-advanced

?? I still don't know how to do this through IAM

'Manual' way:

1. SSH into VM using Google Cloud Console (web browser window)

2. Generate new key with username and an easy identifiable name:
	`ssh-keygen -t rsa -f ~/.ssh/[KEY_FILENAME] -C [USERNAME]`

	like: `ssh-keygen -t rsa -f ~/.ssh/id_gcloud -C paul_broek`

3. Restrict private key access  
 	`cmhod 400 ~/.ssh/id_gcloud`

4. Copy public key contents to Google Cloud `Metadata` section ⟶ `SSH Keys`

5. In a local terminal, copy private key file from remote VM to `~/.ssh` folder

6. Now you can SSH into the remote VM from local terminal  
	`ssh -i ~/.ssh/id_gcloud username@external-ip`

### 1.3 Update `gcloud` sdk

Sometimes new features are released with a new version of gcloud sdk, to update, run: 
```bash
gcloud components update
source ~/.zshrc
```

## 2 Managing images

### 2.1 List popular machine images

```bash
gcloud compute images list
```

### 2.2 List your machine images

```bash
gcloud beta compute machine-images list
```

### 2.3 Create a machine image

```bash
gcloud beta compute machine-images create ubuntu20-basic-1 --project=ob-train --source-instance=ubuntu20-basic --source-instance-zone=us-central1-a --storage-location=us
```

If you don't know the command, try it out in google cloud console, and press in the footer bar **equivalent command line**

### 2.4 Delete a machine image

```bash
gcloud beta compute machine-images delete ubuntu20-basic-1
```

### 2.5 Costs

The cost of having a custom machine image is $0.050 per GB per month. So a 15GB image costs you 0.75$ per month. Therefore, keep just one image and delete the older one.
There are ways to save images to Cloud Storage (costing 2 cents per GB per month), see [this](https://stackoverflow.com/questions/59723073/how-to-download-a-google-cloud-compute-engine-vm-instance)  
And you can then copy the image to a local machine. Instructions of this process:  

1. Export image to Cloud Storage with `gcloud compute images export`:  
	```bash
	gcloud compute images export  \
    --destination-uri gs://ob-train-129933/my-image-file.tar.gz  \
    --image 'conda-plus-private-repos-rclone2'
	```

2. Download the image to your local machine with `gsutil cp`:  
	`gsutil cp gs://ob-train-129933/my-image-file.tar.gz /local/path/to/file`

But best is to keep image size low, increase disk size in very small 1 or 2 GB steps, and keep only one image.

## 3 Managing instances

### 3.1 List instances

```bash
gcloud compute instances list
```

### 3.2 Stop an instance / all instances

```bash
gcloud beta compute instances stop 'ubu20' --zone 'us-central1-a'
```

Iterate over list? CLI does not have a 'stop all' method
```bash
...
```

### 3.3 (Re)start an instance

```bash
gcloud beta compute instances start 'ubu20' --zone 'us-central1-a'
```

## 4 Managing buckets / storage

### 4.1 Working with the `gsutil` tool

More Medium [help](https://medium.com/google-cloud/google-cloud-storage-tutorial-part-1-aee81f9d3247)  
Official [help](https://cloud.google.com/storage/docs/gsutil)
 
```bash
# Create a bucket:
gsutil mb gs://gwbucket
# Create bucket and connect it to a project
gsutil mb -p 'ob-train' -b on gs://ob-train-129933
# Copy some files to the bucket:
gsutil cp *.jpg gs://gwbucket
# List the files in the bucket:
gsutil ls -l gs://ob-train-129933
# Copy a file from our bucket back to the local /tmp directory
gsutil cp gs://gwbucket/sunset.jpg /tmp
# Delete the files:
gsutil rm gs://gwbucket/*
# Remove the bucket:
gsutil rb gs://gwbucket
# Turn on versioning for the bucket
gsutil versioning set on gs://gwnewbucket
# rsync the current directory to our new bucket
# Adding -m to run multiple parallel processes (speed boost)
gsutil -m rsync -r -d . gs://gwnewbucket
```

### 4.2 Increase gcloud storage

See a list of available disks (some instance should be running)

```bash
gcloud compute disk list
```

Increase the disk size of an instance

```bash
gcloud compute disks resize 'ubu20' --zone 'us-central1-a' --size 22
```

## 5 Port forwarding

```bash
# Create a new firewall rule that allows INGRESS tcp:8080 with VMs containing tag 'allow-tcp-8080'
gcloud compute firewall-rules create rule-allow-tcp-8080 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8080 --allow tcp:8080
gcloud compute firewall-rules create rule-allow-tcp-8888 --source-ranges 0.0.0.0/0 --target-tags allow-tcp-8888 --allow tcp:8888

# list your VMs
gcloud compute instances list

# Add the 'allow-tcp-8080' tag to a VM named VM_NAME
gcloud compute instances add-tags VM_NAME --tags allow-tcp-8080
gcloud compute instances add-tags VM_NAME --tags allow-tcp-8888

# remove a rule
gcloud compute instances remove-tags VM_NAME --tags allow-tcp-8888

# If you want to list all the GCE firewall rules
gcloud compute firewall-rules list

# listing active rules by instance?
# --> not possible yet. use GUI console, press on the three dots and click 'View network details'
```

## 6 Billing

**These steps are important to keep your Compute Engine costs low**

Some things to set up:

- Export billing to BigQuery. Follow: https://cloud.google.com/billing/docs/how-to/export-data-bigquery-setup 
- Basically go to console.cloud.google.com -> Billing -> Billing export, and select one of three (currently I use middle option: `detailed usage cost`)

Things to be aware of:

* It might take up to 48 hours to start seeing Google Cloud pricing data in your data table
* After you enable pricing export, the pricing data applicable to your Cloud Billing account is exported to BigQuery **once each day**.
* If you're interested in exporting resource-level cost data to BigQuery for analysis, consider enabling the [detailed usage cost data](https://cloud.google.com/billing/docs/how-to/export-data-bigquery-tables#detailed-usage-cost-data-schema).