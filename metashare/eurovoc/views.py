from metashare.eurovoc import eurovoc
from django.http import HttpResponse

def update_subdomains(request):
    domain = request.POST.get('domain')
    subdomains = eurovoc.get_subdomains_by_domain(domain)
    return HttpResponse("//".join(subdomains))