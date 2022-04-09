import requests as req
from parsel import Selector
import aria2p
import time

download_path = 'D:\\chia\\plotdl'
max_concurrent_downloads = 1
max_connections_per_file = 5

plot_manager_urls = [
    'http://example.ingress.sfo.computer',
]

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
        'max-concurrent-downloads': str(max_concurrent_downloads)
    })
    try:
        while True:
            plot_manager_files = []
            for url in plot_manager_urls:
                plot_manager_files.extend(get_plot_manager_files(url))
            
            s_s = '' if len(plot_manager_files) == 1 else 's'
            print(f'Got {len(plot_manager_files)} file{s_s} from plotmanager')

            check_files(plot_manager_files)

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
        direct_urls.append(link)
    return direct_urls

def check_files(plot_manager_files):

    downloads = aria2.get_downloads()


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
        
        if not already_added:
            print(f'Adding {filename} to downloads')
            aria2.add(link, options={
                'dir': download_path,
                'split': str(max_connections_per_file),
                'max-connection-per-server': '10'})
        else:
            print(f'File has already been added')



    if len(downloads) > 0:
        print('')
        print('Current Downloads')
        print('=================')

    for download in downloads:
        print(f'{download.gid}  {download.status}  {download.progress_string()}  {download.eta_string()}')
        print(f'NAME: {download.name}')

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

        
    

main()