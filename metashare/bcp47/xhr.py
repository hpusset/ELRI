from django.http import HttpResponse

from metashare.bcp47 import iana

def update_lang_variants(request):
    lang = request.POST.get('lang')
    variants = iana.get_variants_by_language(lang)
    return HttpResponse("//".join(variants))

def update_lang_variants_with_script(request):
    lang = request.POST.get('lang')
    script = request.POST.get('script')
    variants = iana.get_variants_by_script(script, lang)
    return HttpResponse("//".join(variants))

def update_var_variants(request):
    print request.POST
    variant = request.POST.get('variant')
    variants = iana.get_variants_by_variant(variant)
    print variant, variants
    return HttpResponse("//".join(variants))
