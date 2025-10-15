import os

# This file is intended to be used for local testing only and should not be committed to git.
# It is recommended to set these values in your environment for CI/CD.

# Default password for test users.
# You can override this by setting the TEST_USER_PASSWORD environment variable.
TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'ComplexDefaultTestPass!23')

# Default password for admin test users.
# You can override this by setting the TEST_ADMIN_PASSWORD environment variable.
TEST_ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', 'ComplexDefaultAdminPass!23')
