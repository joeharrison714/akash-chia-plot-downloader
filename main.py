import requests as req
from parsel import Selector
import aria2p
import time
from urllib.parse import urlparse

max_concurrent_downloads = 2
max_connections_per_file = 5
max_same_server = 1

download_paths = [
    'D:\\chia\\portable-plots',
    'E:\\chia\\portable-plots',
]

plot_manager_urls = [
    'http://example.ingress.sfo.computer',
]

# if set to false, won't actually add any new files to download to aria. Used in rare situations.
add_new = True

# initialization, these are the default values
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret=""
    )
)


def main():
    #print(aria2.get_global_options())

    aria2.set_global_options(options={
        'max-concurrent-downloads': str(max_concurrent_downloads),
    })
    try:
        while True:
            try:
                plot_manager_files = []
                for url in plot_manager_urls:
                    try:
                        plot_manager_files.extend(get_plot_manager_files(url))
                    except:
                        print(f'Error getting plots from: {url}')
                
                s_s = '' if len(plot_manager_files) == 1 else 's'
                print(f'Got {len(plot_manager_files)} file{s_s} from plotmanager')

                check_files(plot_manager_files)
            except:
                print('Error in main loop')

            print('Sleeping...')
            time.sleep(60)
    except KeyboardInterrupt:
        print('interrupted!')

def get_plot_manager_files(url):
    print(f'Fetching files on plot manager from {url}')
    resp = req.get(url)

    # HTML parsing
    page = Selector(text=resp.text)

    links = page.css('a[title="Direct link"]::attr(href)').getall()

    direct_urls = []
    for link in links:
        if link.endswith('.log'):
            print(f'Skipping {link}')
            continue
        direct_urls.append(link)
    return direct_urls

def check_files(plot_manager_files):

    downloads = aria2.get_downloads()

    downloads_by_host = {}
    for download in downloads:
        download_url = download.files[0].uris[0]["uri"]
        url_info = urlparse(download_url)
        host = url_info.hostname

        if not host in downloads_by_host:
            downloads_by_host[host] = 0
        downloads_by_host[host] += 1

    print('')
    print('Plot Manager Files')
    print('==================')
    for link in plot_manager_files:
        filename = link.split('/')[-1]
        print(f'Checking file: {filename}')

        already_added = False
        for download in downloads:
            if download.name == filename:
                already_added = True
                break

        if already_added:
            print(f'File has already been added')
            continue
        
        url_info = urlparse(link)
        host = url_info.hostname

        if host in downloads_by_host:
            cur = downloads_by_host[host]
            if cur >= max_same_server:
                print(f'Waiting to add due to {cur} in-progress downloads from same server')
                continue

        if add_new:
            print(f'Adding {filename} to downloads')
            aria2.add(link, options={
                'dir': get_next_download_path(),
                'split': str(max_connections_per_file),
                'max-connection-per-server': '10'})
        else:
            print(f'Skipping add of {filename} due to add new being turned off')



    if len(downloads) > 0:
        print('')
        print('Current Downloads')
        print('=================')

    for download in downloads:
        print(f'{download.gid}  {download.status}  {download.progress_string()}  {download.eta_string()}')
        print(f'NAME: {download.name}')
        print(f'DIR: {download.dir}')

        url = download.files[0].uris[0]["uri"]
        print(f'URL: {url}')

        if download.status == 'complete':

            is_in_plot_manager = False
            for link in plot_manager_files:
                filename = link.split('/')[-1]
                url = link.rsplit('/', 1)[0]

                if  download.name == filename:
                    is_in_plot_manager = True
                    break

            if is_in_plot_manager:
                print(f'Removing {download.name} from plot manager')
                url_parts = url.split('?')
                base_url = url_parts[0]
                if not base_url.endswith('/'): base_url = f'{base_url}/'
                delete_url = f'{base_url}?p=&del={download.name}'
                del_resp = req.get(delete_url)
                print(del_resp)
                print(del_resp.status_code)
            else:
                print(f'{download.name} is gone from plot manager, deleting from aria')
                aria2.remove([download])
        elif download.status == 'error':
            aria2.remove([download])
        print('-------------------------------------------------')

next_download_path_index = 0

def get_next_download_path():    
    global next_download_path_index

    download_path = download_paths[next_download_path_index]

    next_download_path_index += 1

    if next_download_path_index >= len(download_paths): next_download_path_index = 0

    return download_path


main()
