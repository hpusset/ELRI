import zipfile

from django.utils.encoding import smart_str

from metashare.repository.models import resourceInfoType_model
from metashare.repository.model_utils import get_resource_dataformats

from connector import connect
from lxml import etree

SESSION = connect("tmx_test2")

tmx_resources = list()

# filter(storage_object__publication_status='p')
for r in resourceInfoType_model.objects.all():
    if "TMX" in get_resource_dataformats(r):
        tmx_resources.append(r)


def add_to_basex():
    for obj in tmx_resources:
        print "{}".format(obj)
        archive_path = obj.storage_object.get_download()

        if archive_path:
            zip = zipfile.ZipFile(archive_path)

            count = 0
            for f in zip.namelist():
                if f.endswith(".tmx"):
                    if len(zip.namelist()) > 1:
                        count += 1
                    fl = zip.open(f)
                    out_filename = "{}".format(str(obj.id))
                    if count:
                        out_filename += "_{}".format(str(count))
                    content = fl.read()
                    try:
                        print "\tAdding \'{}\' to xml database".format(smart_str(f))
                        etree.fromstring(content)
                        SESSION.add("test_tmx2/{}".format(out_filename), content)
                    except:
                        print "\t\tERROR: Resource \"{}\" with ID {} could not be added to Database.\n" \
                              "\t\tPlease check the respective files for well-formedness.\n".format(obj, obj.id)
                    finally:
                        fl.close()
