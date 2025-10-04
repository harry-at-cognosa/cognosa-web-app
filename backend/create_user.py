###
# Create user
# command-line options:
# -e email@example.com
# -p password
# -u user_name. Must be unique, lower case, letters numbers and underscore or hyphen no spaces or special characters.
# -f full_name. Use double quotes.
# -g group_id. Not required. Default: 2
# -s is_superuser. Not required. Default: False
# -v is_verified. Not required. Default: False
# -ga is_groupadmin. Not required. Default: False
# -cm is_contentmanager. Not required. Default: False
# -na is inactive. Not required: Default: False (means is_active = True)
# Example:
# python3 .\create_user.py -e john_smith@example.com -p 12345678 -f "John Smith" -s
###
import argparse
import asyncio
from cwa_lib.sql_tables.api_users import ApiUsersTable


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a user with given parameters.")

    parser.add_argument("-e", "--email", required=True, type=str, help="User email")
    parser.add_argument("-p", "--password", required=True, type=str, help="User password")
    parser.add_argument("-u", "--user_name", required=True, type=str, help="user_name")
    parser.add_argument("-f", "--full_name", required=True, type=str, help="Full name")
    parser.add_argument("-g", "--group_id", type=int, default=2, help="Group ID")
    parser.add_argument("-s", "--is_superuser", action="store_true", help="Is the user a superuser (default: False)")
    parser.add_argument("-na", "--is_inactive", action="store_true", help="If set, user is inactive (default: False)")
    parser.add_argument("-v", "--is_verified", action="store_true", help="If set, user is verified (default: False)")
    parser.add_argument("-ga", "--is_groupadmin", action="store_true", help="If set, user is groupadmin (default: False)")
    parser.add_argument("-cm", "--is_contentmanager", action="store_true", help="If set, user is contentmanager (default: False)")
    
    args = parser.parse_args()

    try:
        asyncio.run(ApiUsersTable.create_user(
            user_id=None,
            email=args.email,
            password=args.password,
            user_name=args.user_name,
            full_name=args.full_name,
            group_id=args.group_id,
            is_active=not args.is_inactive,
            is_verified=args.is_verified,
            is_superuser=args.is_superuser,
            is_groupadmin=args.is_groupadmin,
            is_contentmanager=args.is_contentmanager,
            ))
    except Exception as exc:
        print(exc)
