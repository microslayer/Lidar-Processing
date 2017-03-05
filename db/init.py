#!/usr/bin/python

def config():
    """
        Function provides the parameters for postgres database
    """
    params ={}
    params['host'] = "localhost"
    params['dbname'] = 'lidar'
    params['user'] = 'postgres'
    params['password'] = 'xxxxx'
    return params


if __name__ == '__main__':
    k = config()
    #print(k['h-'])