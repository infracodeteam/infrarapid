import sys


AWS = """
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_force_path_style         = true
"""
AZURE = """
    skip_credentials_validation = true
    skip_provider_registration = true
"""

PROVIDER_FILE = sys.argv[1] if len(sys.argv) > 1 else "main.tf"

with open(PROVIDER_FILE) as f:
    new_lines = []
    for line in f:
        new_lines.append(line)
        if 'provider "aws"' in line:
            new_lines.append(AWS)
        if 'provider "azurerm"' in line:
            new_lines.append(AZURE)

with open(PROVIDER_FILE, "w") as f:
    f.writelines(new_lines)
