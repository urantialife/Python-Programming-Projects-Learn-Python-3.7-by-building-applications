from csv import DictReader, DictWriter
from time import sleep
import argparse

import requests
from tqdm import tqdm

 
base_url = 'https://nominatim.openstreetmap.org/search?'
 
def nominatim_geocode(address, format='json', limit=1, **kwargs):
    '''thin wrapper around nominatim API.
 
    Documentation: https://wiki.openstreetmap.org/wiki/Nominatim#Parameters
    '''
    params = {'q':address, 'format':format, 'limit':limit, **kwargs}
 
    response = requests.get(base_url, params=params)
    response.raise_for_status() # will raise exception if status is unsuccessful
 
    sleep(1) # sleep 
    return response.json()


def read_csv(path):
    '''read csv and return it as a list of dictionaries, one per row'''
    with open(path, 'r') as f:
        return list(DictReader(f))


def write_csv(data, path, mode='w'):
    '''write data to csv or append to existing one'''
    if mode not in 'wa':  # 'a' mode will append to the existing file, if it exists
        raise ValueError("mode should be either 'w' or 'a'")  
    
    with open(path, mode) as f:
        writer = DictWriter(f, fieldnames=data[0].keys())
        if mode == 'w':
            writer.writeheader() 

        for row in data:
            writer.writerow(row)  
            

def geocode_bulk(data, column='address', verbose=False):
    '''assuming data is an iterable of dicts, will attempt to geocode each,
    treating {column} as an address. Returns 2 iterables - result and errored rows'''
    result, errors = [], []

    for row in tqdm(data):
        try:
            search = nominatim_geocode(row[column], limit=1)
            if len(search) == 0: # no location found:
                result.append(row)
                if verbose:
                    print(f"Can't find anything for {row[column]}")
                    
            else:
                info = search[0]  # most "important" result
                info.update(row)  # merge two dicts
                result.append(info) 
        except Exception as e:
            if verbose:
                print(e)
            row['error'] = e
            errors.append(row)
    
    if len(errors) > 0 and verbose:
        print(f'{len(errors)}/{len(data)} rows failed')

    return result, errors

def main(args):
    data = read_csv(args.path_in)
    result, errors = geocode_bulk(data, column=args.column, verbose=True)
    write_csv(result, args.path_out)


print(nominatim_geocode('13 Rue de la Chapelle, 70250 Ronchamp, France'))

# if __name__ == '__main__':
#     parser=argparse.ArgumentParser()
#     parser.add_argument('--path_in', help='path to the input csv file')
#     parser.add_argument('--path_out', help='path to the output csv file',
#                         default='geocoded_data.csv')
    
#     parser.add_argument('--column', 
#                         help='column with the address in the input csv file',
#                         default='address')

#     args=parser.parse_args()
#     main(args)