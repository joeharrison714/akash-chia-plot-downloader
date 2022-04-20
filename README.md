# akash-chia-plot-downloader

This is a script that will automatically download plots from the Akash "Chia Plot Manager" and delete them when the download is complete. The script interacts with the aria2 download manager to do the actual transfers.

## Settings
|Name|Description|
|------------------------|----------------|
|max_concurrent_downloads|Aria2 setting controlling the maximum number of concurrent downloads|
|max_connections_per_file|Aria2 setting controlling number of connections to make per download|
|max_same_server|Controls number of downloads to add to aria2 from the same host|
|download_paths|The local paths to download the plots to. If multiple are provided they will be used in a round-robin fashion.
|plot_manager_urls|The urls of the plot manager interface|


## Setup
1. Create venv: `python -m venv venv`
1. Activate venv
1. `pip -r requirements.txt`
1. Download aria2 from: https://github.com/aria2/aria2

## Running
1. Fill in the plot manager URLs
1. Fill in the download locations
1. Run aria2c in RPC mode by executing: `aria2c.exe --enable-rpc`
1. Run `main.py`
