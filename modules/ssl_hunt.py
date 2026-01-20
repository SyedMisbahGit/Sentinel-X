#!/usr/bin/env python3
import sys, ssl, socket
def get_cert_serial(hostname):
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with ssl.create_default_context().wrap_socket(sock, server_hostname=hostname) as ssock:
                return ssock.getpeercert().get('serialNumber')
    except: return None

if __name__ == "__main__":
    serial = get_cert_serial(sys.argv[1])
    if serial:
        print(f"\n\033[94m[+] SSL SERIAL: {serial}\033[0m")
        print(f"    -> Censys: https://search.censys.io/search?resource=hosts&q=services.tls.certificates.leaf_data.serial_number%3A{serial}")
        print(f"    -> Shodan: https://www.shodan.io/search?query=ssl.cert.serial:{serial}")
