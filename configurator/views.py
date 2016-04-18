from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import render 
from django.template import RequestContext


def main(request):

    return render_to_response(
        'configurator/index.html',
        {},
        context_instance=RequestContext(request)
    )


def async_call():
    print("Method reached!")
