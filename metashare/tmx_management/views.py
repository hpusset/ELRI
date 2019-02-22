import os
from StringIO import StringIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import datetime

from connector import connect
from metashare.tmx_management.forms import TmxQueryForm

SESSION = connect("tmx_test")


@login_required
def db_info(request):
    return HttpResponse(SESSION.execute("INFO DB").replace("\n", "<br/>"))


@login_required()
def get_by_lang_pair(request):
    l1 = request.GET['l1']
    l2 = request.GET['l2']

    query_string = None

    # read the predefined xquery file
    with open(os.path.join(os.path.dirname(__file__), 'queries/get_tus_by_lang_pair.xq'), 'r') as xq:
        query_string = xq.read()

    query = SESSION.query(str(query_string % (l1, l2, l1, l2)))

    in_memory = StringIO()

    #output_filename = "ELRC-SHARE_{}-{}_{}.tmx".format(l1, l2, datetime.date.today())
    output_filename = "ELRI_{}-{}_{}.tmx".format(l1, l2, datetime.date.today())
    print output_filename
    in_memory.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    for typecode, item in query.iter():
        # print("typecode=%d" % typecode)
        in_memory.write(item.encode('utf-8'))
    query.close()

    if in_memory.len < 100:
        return HttpResponse("Your query did not return any translation units")

    response = HttpResponse(content_type="application/xml")
    response['Content-Disposition'] = \
        'attachment; filename=%s' % (output_filename)
    in_memory.seek(0)
    response.write(in_memory.read())
    in_memory.close()
    return response

def tmx_query(request):
    form = TmxQueryForm()

    return form
