import json

import indy_community.agent_utils as agent_utils

from indy_community import models as indy_models

from atriacalendar.models import *


# once connection is confirmed at both ends, activate the Atria relationship
def activate_atria_connection(connection):
    # find atria relationship
    if connection.wallet.wallet_org.get():
        org = connection.wallet.wallet_org.get()
        neighbour = User.objects.filter(email=connection.partner_name).get()
    else:
        neighbour = connection.wallet.wallet_user.get()
        org = AtriaOrganization.objects.filter(org_name=connection.partner_name).get()
    existing_relations = AtriaRelationship.objects.filter(org=org, user=neighbour, relation_type__relation_type='Member').all()
    if 0 < len(existing_relations):
        existing_relations[0].status='Active'
        existing_relations[0].save()


def dummy_fn(conversation, prev_type, prev_status, owner):
    #print("dummy_fn()", conversation.conversation_type, prev_type, prev_status, owner)
    pass


def association_issue_credential(conversation, prev_type, prev_status, owner):
    print("association_issue_credential()", conversation.conversation_type, prev_type, prev_status, owner)

    # if prev_state = CredentialOffer then we are issuing the credential
    if prev_type == "CredentialOffer":
        conversation_data = json.loads(conversation.conversation_data)
        attrs = conversation_data['data']['credential_attributes']
        member = AtriaRelationship.objects.filter(relation_type__relation_type='Member', status='Active', user__email=conversation.connection.partner_name, org__wallet=conversation.connection.wallet).get()
        indy_offer = json.loads(conversation_data['data']['credential_offer']['libindy_offer'])
        schema_id = indy_offer['schema_id']
        schema = IndySchema.objects.filter(ledger_schema_id=schema_id).get()
        certification = MemberCertification(
                member = member,
                certification_type = schema,
                reference = conversation,
                certification_data = attrs
            )
        certification.save()

    # if prev_state = IssueCredential then credential has been accepted
    if prev_type == "IssueCredential":
        pass


def association_receive_proof(conversation, prev_type, prev_status, owner):
    print("association_receive_proof()", conversation.conversation_type, prev_type, prev_status, owner)

    # proof received from neighbour
    conversation_data = json.loads(conversation.conversation_data)
    member = AtriaRelationship.objects.filter(relation_type__relation_type='Member', status='Active', user__email=conversation.connection.partner_name, org__wallet=conversation.connection.wallet).get()
    indy_proof = json.loads(conversation_data['data']['proof']['libindy_proof'])
    proof = indy_proof['requested_proof']
    # TODO we can have more than one identifier
    schema_id = indy_proof['identifiers'][0]['schema_id']
    schema = IndySchema.objects.filter(ledger_schema_id=schema_id).get()
    certification = MemberCertification(
            member = member,
            certification_type = schema,
            reference = conversation,
            certification_data = proof
        )
    certification.save()


# TODO create any necessary functions for this dispatch table
DISPATCH_TABLE = {
    'Org': {
        # "Association" is one of the neighbourhood houses or community centers
        'Association': {
            # Won't receive Credential Offers
            #'CredentialOffer': dummy_fn,
            # When we receive a Cred Request (and issue the Credential) save ourselves a copy
            'IssueCredential': association_issue_credential,
            # Receive proof response from neighbour, save this as a "proven" credential
            'ProofRequest': {
                #'Pending': dummy_fn,
                'Accepted': association_receive_proof
            }
        },
        # "Admin" is sitting this one out for now ... TBD
        'Admin': {
            # Imms Repository will auto-receive credentials
            #'CredentialOffer': repository_auto_accept_credential_offers,
            # no special handling when credentials are received
            #'CredentialRequest': repository_auto_receive_credentials,
            # Receive proof request from School, or receive Proof from Parent
            #'ProofRequest': {
            #    'Pending': repository_auto_answer_proof_requests,
            #    'Accepted': repository_auto_receive_proofs
            #},
            #'Connection': repository_auto_answer_connections
        }
    },
    'User': {
        # Check for consent offer credentials
        'CredentialOffer': dummy_fn,
        # Check for consent-related proof requests from School and Imms Repo
        'ProofRequest': {
            'Pending': dummy_fn,
        }
    }
}

# dispatcher
def conversation_callback(conversation, prev_type, prev_status):
    print(conversation.conversation_type, prev_type, prev_status)

    # skip dispatching if nothing has changed
    conversation_type = conversation.conversation_type
    status = conversation.status
    if prev_type and prev_status and (conversation_type == prev_type) and (status == prev_status):
        return

    # determine dispatch function
    dispatch_fn = None
    org = None
    user = None
    if conversation.connection.wallet.wallet_org and 0 < len(conversation.connection.wallet.wallet_org.all()):
        org = conversation.connection.wallet.wallet_org.all()[0]
        role_name = org.role.name
        dispatch = DISPATCH_TABLE['Org']
        if role_name in dispatch:
            dispatch = dispatch[role_name]
        else:
            dispatch = {}
    elif conversation.connection.wallet.wallet_user and 0 < len(conversation.connection.wallet.wallet_user.all()):
        user = conversation.connection.wallet.wallet_user.all()[0]
        dispatch = DISPATCH_TABLE['User']
    else:
        # ignore un-owned wallets
        dispatch = {}

    if conversation_type in dispatch:
        dispatch = dispatch[conversation_type]
        if isinstance(dispatch, dict):
            if status in dispatch:
                dispatch = dispatch[status]
                dispatch_fn = dispatch
        else:
            dispatch_fn = dispatch

    if dispatch_fn:
        print("Dispatching ...")
        if org:
            dispatch(conversation, prev_type, prev_status, org)
        elif user:
            dispatch(conversation, prev_type, prev_status, user)
        else:
            print("Can't dispatch, no org or user found")
    else:
        print("Skipping ...")


# dispatcher
def connection_callback(connection, prev_status):
    print("connection callback", prev_status, connection.status)

    status = connection.status
    if prev_status and (status == prev_status):
        return

    if connection.connection_type == 'Outbound' and connection.status == 'Active':
        # make Atria connection active as well
        activate_atria_connection(connection)


