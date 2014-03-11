#!/bin/bash

# For testing with local database.
# Run with ". ./set_database_url.sh"
export DATABASE_URL="postgres://drewdez@localhost/funicular"
echo "DATABASE_URL set to $DATABASE_URL"