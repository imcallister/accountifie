"""
Adapted with permission from ReportLab's DocEngine framework

An easy way to provide useful stats.  Put a module like this in your app, with whatever
queries or callables you want in it.  They should return list-of-lists structures.


"""

SQL_QUERIES = [
    [
    'all_users',
    'lists all user names and email addresses',
    'SELECT id, username, email, is_staff, is_superuser FROM auth_user'
    ],

]