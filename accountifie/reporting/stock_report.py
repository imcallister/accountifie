'''
dummy module to allow rlgendoc to work and acknowledge the app_name and 
at the same time not require another prep file
'''
from accountifie.common.makepdf import rlgendoc

@rlgendoc
def finreport(*args, **kwargs):
    return kwargs

