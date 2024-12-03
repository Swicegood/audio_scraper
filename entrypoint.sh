#!/bin/bash
# Set up the SSH key
echo "$SSH_PRIVATE_KEY" > id_rsa_atourcity
chmod 600 id_rsa_atourcity

# Run any initial commands (like SSH)
ssh -o StrictHostKeyChecking=no -i id_rsa_atourcity atourcity@newgoloka.com


# Execute the passed command
exec "$@"
