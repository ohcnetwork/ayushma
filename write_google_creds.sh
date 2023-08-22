#!/bin/bash
echo ${GOOGLE_APPLICATION_CREDENTIALS_B64} | base64 -d > gc_credential.json
