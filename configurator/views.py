from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.utils.translation import ugettext as _

# Create your views here.

def main(request):

	return render_to_response(
            'configurator/index.html',
            {},
            context_instance=RequestContext(request)
    )
