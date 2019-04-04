import os
import datetime
import platform

from .settings import *


INDY_CONFIG['storage_dll']    = 'libindystrgpostgres' + file_ext()
INDY_CONFIG['payment_dll']    = 'libnullpay' + file_ext()
INDY_CONFIG['storage_config'] = {'url': 'wallet-db:5432'}
INDY_CONFIG['vcx_agency_url'] = 'http://dummy-cloud-agent:8080'
INDY_CONFIG['vcx_genesis_path'] = '/tmp/atria-genesis.txt'
INDY_CONFIG['ledger_url']      = 'http://webserver:8000'
INDY_CONFIG['vcx_genesis_url'] = 'http://webserver:8000/genesis'

