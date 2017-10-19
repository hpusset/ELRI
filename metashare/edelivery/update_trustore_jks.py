import jks

from metashare.edelivery.update_ap_files import update_trustore
from metashare.local_settings import TRUSTORE_FILE, TRUSTSTORE_PASSWORD


def update_trustore_keystore():
    ks = jks.KeyStore.load(TRUSTORE_FILE, TRUSTSTORE_PASSWORD)

    new = jks.TrustedCertEntry.new("uni_gw", open('metashare/edelivery/ap_certs/uni.cer', 'rb').read())

    ks.entries['uni_gw'] = new
    ks.save(TRUSTORE_FILE, TRUSTSTORE_PASSWORD)

    update_trustore(TRUSTORE_FILE)