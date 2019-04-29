import os
import datetime
import platform

from .settings import *


INDY_CONFIG['storage_dll']    = 'libindystrgpostgres' + file_ext()
INDY_CONFIG['payment_dll']    = 'libnullpay' + file_ext()
INDY_CONFIG['storage_config'] = {'url': 'wallet-db:5432'}
# from VCX [SERVER_ENVIRONMENT.STAGING] config (connector-app/app/store/config-store.js)
#INDY_CONFIG['vcx_agency_url'] = 'http://dummy-cloud-agent:8080'
#INDY_CONFIG['vcx_agency_url'] = 'http://vcx-agency.anon-solutions.ca:8080'
INDY_CONFIG['vcx_agency_url'] = 'https://agency.pstg.evernym.com'
INDY_CONFIG['vcx_agency_did'] = 'LqnB96M6wBALqRZsrTTwda'
INDY_CONFIG['vcx_agency_verkey'] = 'BpDPZHLbJFu67sWujecoreojiWZbi2dgf4xnYemUzFvB'
INDY_CONFIG['vcx_genesis_path'] = '/tmp/stn-genesis.txt'
# TBD not sure if there is an STN browser available
INDY_CONFIG['ledger_url']      = 'http://sovrin-stn-browser.vonx.io'
INDY_CONFIG['vcx_genesis_url'] = 'https://raw.githubusercontent.com/sovrin-foundation/sovrin/stable/sovrin/pool_transactions_sandbox_genesis'
# on STN, DID's must be pre-registered (based on seed)
INDY_CONFIG['register_dids'] = False

