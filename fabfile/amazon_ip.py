from subprocess import *

dir = "fabfile/amazonctl/"


def get_external_ips(type):
    out = Popen(["%sec2externalips" % dir, type], stdout=PIPE).communicate()[0]
    print "%s %s external IPs: %s"  % (out.count('\n'), type ,out.replace("\n",", "))
    return out


def get_internal_ips(type):
    out = Popen(["%sec2internalips" % dir, type], stdout=PIPE).communicate()[0]
    print "%s %s internal IPs: %s"  % (out.count('\n'), type ,out.replace("\n",", "))
    return out






