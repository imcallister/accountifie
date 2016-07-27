
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.reporting.importers import order_upload
from accountifie.toolkit.forms import FileForm
import accountifie.toolkit

@login_required
def upload_file(request, file_type, check=False):

    if request.method == 'POST':
        if file_type == 'metrics':
            return order_upload(request)
        else:
            raise ValueError("Unexpected file type; know about metrics")
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render_to_response('common/upload_csv.html', context, context_instance=RequestContext(request))
