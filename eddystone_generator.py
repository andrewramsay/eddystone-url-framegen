import sys

PREFIX_ENCODINGS = \
{
    'http://www.'   : 0x00,
    'https://www.'  : 0x01,
    'http://'       : 0x02,
    'https://'      : 0x03,
}

URL_ENCODINGS = \
{
    '.com/' : 0x00,
    '.org/' : 0x01,
    '.edu/' : 0x02,
    '.net/' : 0x03,
    '.info/': 0x04,
    '.biz/' : 0x05,
    '.gov/' : 0x06,
    '.com'  : 0x07,
    '.org'  : 0x08,
    '.edu'  : 0x09,
    '.net'  : 0x0a,
    '.info' : 0x0b,
    '.biz'  : 0x0c,
    '.gov'  : 0x0d
}

def encode_url(url):
    encoded = []
    # replace the prefix with the encoded version if possible
    for prefix in PREFIX_ENCODINGS:
        if url.startswith(prefix):
            encoded.append(PREFIX_ENCODINGS[prefix])
            url = url[len(prefix):]

    if len(encoded) == 0:
        print('Unknown/unsupported URL prefix found')
        sys.exit(-1)

    # TODO support URL_ENCODINGS
    for u in url:
        encoded.append(ord(u))

    return encoded

def generate_frame(url):
    frame = []

    # - length (complete list of 16-bit services UUIDs)
    # - "Complete list" data type value (0x03)
    # - 16-bit Eddystone UUID (0xFEAA, big endian!)
    # - 2nd part of 16-bit Eddystone UUID
    frame.append(0x03)
    frame.append(0x03)
    frame.append(0xAA)
    frame.append(0xFE)

    # encode the URL into Eddystone format
    encoded_url = encode_url(url)

    # - Length of Service Data (encoded URL size + 5 header bytes)
    # - "Service Data" data type value (0x16)
    # - 16-bit Eddystone UUID
    # - 2nd part of 16-bit Eddystone UUID
    frame.append(len(encoded_url) + 5)
    frame.append(0x16)
    frame.append(0xAA)
    frame.append(0xFE)
    
    # - frame type (0x10 from Eddystone spec)
    # - tx power (0xEE for eg = -18dBm (this should really be calibrated to give proper distance measurements))
    frame.append(0x10)
    frame.append(0xEE)

    # finally append the encoded URL data
    frame.extend(encoded_url)

    return ''.join(['%02X' % x for x in frame])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: eddystone_generator.py <url>')
        sys.exit(0)

    framedata = generate_frame(sys.argv[1])

    print('0xFFD1 content should be: %s' % framedata[:40])
    print('0xFFD2 content should be: %s' % framedata[40:])
