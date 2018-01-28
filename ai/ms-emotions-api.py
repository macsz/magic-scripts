import httplib
import urllib
import base64
import json
import os
import sys
import requests
import time


def processRequest( json, data, headers, params ):
    retries = 0
    result = None
    while True:
        response = requests.request( 'post', 'https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize', json = json, data = data, headers = headers, params = params )

        if response.status_code == 429: 

            print( "Message: %s" % ( response.json()['error']['message'] ) )

            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
                result = None 
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
                if 'application/json' in response.headers['content-type'].lower(): 
                    result = response.json() if response.content else None 
                elif 'image' in response.headers['content-type'].lower(): 
                    result = response.content
        else:
            print( "Error code: %d" % ( response.status_code ) )
            print( "Message: %s" % ( response.json() ) )

        break
        
    return result


def get_results(img_path):
    with open(img_path, 'rb' ) as f:
        data = f.read()

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = '17f79e351ec2453e8c4723973722e55f'
    headers['Content-Type'] = 'application/octet-stream'

    json = None
    params = None

    try:
        result = processRequest( json, data, headers, params )
    except:
        return 'exception'

    highest_val = -1.0
    highest_label = 'none'

    if len(result) == 1:
        for emotion in result[0]['scores'].keys():
            r = result[0]['scores'][emotion]
            r = int(r*1000)/1000.0
            if r > highest_val:
                highest_val = r
                highest_label = emotion
    else:
        print('No faces found')
        return 'none'
    return highest_label

def main(dir_path):
    dir_list = sorted([os.path.join(dir_path, d) for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))])
    # dir_list = [
    #     # '/home/macsz/datasets/emotions/img/rgb/S02/I04',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V01',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V02',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V03',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V04',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V05',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V06',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V07',
    #     '/home/macsz/datasets/emotions/img/rgb/S02/V08',
    # ]
    print(dir_list)
    # record = False
    for d in dir_list:
        print('Processing dir {0}'.format(d))
        images_list = sorted([os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and f.endswith('.png')])
        file_name = '{0}_{1}.txt'.format(d.split('/')[-2], d.split('/')[-1])
        with open(file_name, 'w') as f:
            for img in images_list:
                # if img.endswith('out73.png'):
                #     record = True
                # if record:
                print('Processing img {0}'.format(img))
                label = get_results(img)
                f.write(label + '\n')
                print(label)
                time.sleep(3)

if __name__ == '__main__':
    main(sys.argv[1])
