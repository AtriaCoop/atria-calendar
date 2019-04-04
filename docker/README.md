# Install and run Django Indy Community

There are two options to run the environment locally - running in docker (recommended) or running all the services locally on "bare metal".


## Running Django Indy Community - Docker Version (recommended)

1. Open two bash shells, and run the following commands:

```bash
git clone https://github.com/bcgov/von-network.git
cd von-network
./manage build
./manage start
```

... and in the second shell:

```bash
git clone https://github.com/AnonSolutions/django-indy-community.git
cd django-indy-community/docker
./base-image      # note that this takes about 30 mintues
./manage start
```

That's it!  Your docker is up and running, open a browser and navigate to http://localhost:8000/

To shut down the environment, CTRL-C to stop the docker services and then in each shell run:

```bash
./manage rm
```


### Running Django Indy Community - "Bare Metal" Version

If you compare to the previous option, these are basically all the steps executed to build the docker environment.

Note it is recommended to build/run on either Ubuntu 16.04 or on the latest Mac o/s.

1. Check out the following github repositories:

```bash
git clone https://github.com/ianco/indy-sdk.git
cd indy-sdk
git checkout master
cd ..
git clone https://github.com/bcgov/von-network.git
```

Note that these are the "ianco" forks of the master repositories as they contain updates/fixes that are not yet PR'ed.

1a. Install dependencies in von-network:

```bash
cd von-network
virtualenv --python=python3.6 venv
source venv/bin/activate
pip install -r server/requirements.txt
```

2. In the indy-sdk repository, build all necessary libraries (Note: check out the [indy-sdk repo](https://github.com/hyperledger/indy-sdk) for dependencies, such as rust):

```bash
cd indy-sdk
cd libindy
cargo build
ln -s target/debug/libindy.so /use/local/lib/
cd ..

cd experimental/plugins/postgres_storage
cargo build
ln -s target/debug/libindystrgpostgres.so /use/local/lib/
cd ../../..

cd cli
cargo build
cd ..

cd libnulpay
cargo build
ln -s target/debug/libnullpay.so /use/local/lib/
cd ..

cd vcx
cd libvcx
cargo build
ln -s target/debug/libvcx.so /use/local/lib/
cd ..

cd dummy-cloud-agent
cargo build
```

3. In the root indy-sdk directory, build and run the indy nodes:

```bash
docker build -f ci/indy-pool.dockerfile -t indy_pool .
docker run -itd -p 9701-9708:9701-9708 indy_pool
```

... and run a postgres database:

```bash
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres -c 'log_statement=all' -c 'logging_collector=on' -c 'log_destination=stderr'
```

4. In a separate shell, run the VCX cloud agent:

```bash
cd indy-sdk/vcx/dummy-cloud-agent
cargo run config.json
```

5. Open 2 shells to run the Django Indy Community edition:

```bash
cd django-indy-community/indy_community_demo
./reload_db.sh
python manage.py runserver
```

... and run the "virtual agent" bot:

```bash
cd django-indy-community/indy_community_demo
python manage.py process_tasks
```

6. Whew!  One more - start up the von-network ledger browser - this also provides the capability to register DID's on the ledger for our Test organizations:

```bash
cd von-network
GENESIS_FILE=/tmp/atria-genesis.txt PORT=9000 python -m server.server
```

Note that the genesis file at the above location is created by Django Indy Community on startup.


### Reset the Django Indy Community environment

To reset the environment and start from scratch:

1. Shut down the von-network ledger browser and vcx dummy-cloud-agent (just CRTL-C to kill each of these processes), and then:

```bash
rm -rf ~/.indy_client/
```

2. Kill the two Django processes (CTRL-C) and reload the Test database:

```bash
cd django-indy-community/indy_community_demo
./reload_db.sh
```

3. Kill the 2 docker processes (indy nodes and postgres database):

```bash
# to kill the 2 specific dockers:
docker ps   # (get the process id's)
docker stop <process 1> <process 2>
docker rm -f <process 1> <process 2>
# ... or to indescriminitely kill all dockers:
docker ps -q  | xargs docker rm -f
```

To re-start the environment, just go to step #1 of the previous section.

