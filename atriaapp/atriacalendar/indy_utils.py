import indy_community.agent_utils as agent_utils


def auto_accept_connection(connection):
    connection_id = connection.connection_id
    wallet = connections.wallet
    partner_name = connections.partner_name
    invitation_details = connections.invitation
    my_connection = agent_utils.send_connection_confirmation(wallet, connection_id, partner_name, invitation_details)


DISPATCH_TABLE = {
    'Org': {
        # Out "HA" is now playing the dual role of "repository" as well
        'role1': {
            # Imms Repository will auto-receive credentials
            'CredentialOffer': repository_auto_accept_credential_offers,
            # no special handling when credentials are received
            'CredentialRequest': repository_auto_receive_credentials,
            # Receive proof request from School, or receive Proof from Parent
            'ProofRequest': {
                'Pending': repository_auto_answer_proof_requests,
                'Accepted': repository_auto_receive_proofs
            }
        },
        'role2': {
            # School has no special processing around receipt of credentials
            # Received proof (upon request) from Individual or from Imms Repo
            'ProofRequest': {
                'Accepted': school_auto_receive_proofs
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
        'CredentialOffer': user_auto_receive_credential_offers,
        # Check for consent-related proof requests from School and Imms Repo
        'ProofRequest': {
            'Pending': user_auto_receive_proof_requests,
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

    if connection.connection_type == 'Inbound' and connection.status == 'Pending':
        # auto-accept requests
        auto_accept_connection(connection)

