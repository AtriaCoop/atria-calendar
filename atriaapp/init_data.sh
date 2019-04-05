python manage.py loads_orgs ./trustee-org.yml
sleep 5
python manage.py loads_schemas ./myco-schemas.yml 1
sleep 5
python manage.py loads_orgs ./myco-orgs.yml
sleep 5
