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


def dummy_fn():
    pass

# TODO create any necessary functions for this dispatch table
DISPATCH_TABLE = {
    'Org': {
        # Out "HA" is now playing the dual role of "repository" as well
        'role1': {
            # Imms Repository will auto-receive credentials
            'CredentialOffer': dummy_fn,
            # no special handling when credentials are received
            'CredentialRequest': dummy_fn,
            # Receive proof request from School, or receive Proof from Parent
            'ProofRequest': {
                'Pending': dummy_fn,
                'Accepted': dummy_fn
            }
        },
        'role2': {
            # School has no special processing around receipt of credentials
            # Received proof (upon request) from Individual or from Imms Repo
            'ProofRequest': {
                'Accepted': dummy_fn
            }
        },
        # "repository" is sitting this one out for now ...
        'role3': {
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


