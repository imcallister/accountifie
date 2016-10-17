
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accountifie.common.uploaders.upload_tools import order_upload
from accountifie.toolkit.forms import LabelledFileForm
import accountifie.reporting.importers

@login_required
def upload_file(request, file_type, check=False):
	if request.method == 'POST':
		if file_type == 'metrics':
			processor = accountifie.reporting.importers.process_metrics
			return order_upload(request,
								processor,
								label=True,
								redirect_url='/projections/parameters/')
		else:
			raise ValueError("Unexpected file type; know about metrics")
	else:
		form = LabelledFileForm()
		context = {'form': form, 'file_type': file_type}
		return render(request, 'common/upload_csv.html', context)
