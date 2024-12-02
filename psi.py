# PSI

import random
from hashlib import blake2b

# Large safe prime P (2048-bit prime from RFC 7919)
P_hex = '''
FFFFFFFF FFFFFFFF ADF85458 A2BB4A9A AFDC5620 273D3CF1
D8B9C583 CE2D3695 A9E13641 146433FB CC939DCE 249B3EF9
7D2FE363 630C75D8 F681B202 AEC4617A D3DF1ED5 D5FD6561
2433F51F 5F066ED0 85636555 3DED1AF3 B557135E 7F57C935
984F0C70 E0E68B77 E2A689DA F3EFE872 1DF158A1 36ADE735
30ACCA4F 483A797A BC0AB182 B324FB61 D108A94B B2C8E3FB
B96ADAB7 60D7F468 1D4F42A3 DE394DF4 AE56EDE7 6372BB19
0B07A7C8 EE0A6D70 9E02FCE1 CDF7E2EC C03404CD 28342F61
9172FE9C E98583FF 8E4F1232 EEF28183 C3FE3B1B 4C6FAD73
3BB5FCBC 2EC22005 C58EF183 7D1683B2 C6F34A26 C1B2EFFA
886B4238 61285C97 FFFFFFFF FFFFFFFF
'''

# Remove spaces and newlines from the hex string and convert it to an integer
P = int(P_hex.replace('\n', '').replace(' ', ''), 16)

# Generator G
G = 2

# Group order q
q = (P - 1) // 2

def hash_to_int(kwd):
    # Hash a keyword to an integer modulo q
    hash_value = blake2b(kwd.encode(), digest_size=64).digest()
    return int.from_bytes(hash_value, 'big') % q

def generate_secret():
    # Generate a random secret exponent less than q
    return random.randint(1, q - 1)

def server_setup():
    # Server's keyword set
    server_keywords = {'doc1': ['apple', 'banana', 'cherry', 'apple'],}

    # Hash/encrypt server's keywords
    server_elements = {doc_id: [hash_to_int(kwd) for kwd in keywords]
                        for doc_id, keywords in server_keywords.items()}

    return server_elements

def client_setup():
    # Client inputs the keywords they wish to search for
    user_input = input("Please enter keywords to search separated by spaces: ").strip()
    client_keywords = [word for word in user_input.split() if word]

    # Hash/encrypt client's keywords to integers
    client_elements = [hash_to_int(kwd) for kwd in client_keywords]

    return client_elements

def client_transform(client_elements):
    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_transformed_elements = [pow(G, elem * client_secret, P) for elem in client_elements]
    return client_secret, client_transformed_elements

def server_process(server_elements, client_transformed_elements):
    server_data = {}
    for doc_id, server_element in server_elements.items():
        # Server generates a secret and exponentiates their hashed elements and then hashes them again
        server_secret = generate_secret()
        server_transformed_elements = []
        for elem in server_element:
            transformed_elem = pow(G, elem * server_secret, P)
            elem_hash = blake2b((str(doc_id) + '||' + str(transformed_elem)).encode(), digest_size=64).hexdigest()
            server_transformed_elements.append(elem_hash)
        # Server exponentiates client's elements with server's secret
        client_elements_server = [pow(elem, server_secret, P) for elem in client_transformed_elements]
        server_data[doc_id] = (server_transformed_elements, client_elements_server)
    return server_data

def client_compute_intersection(client_secret, server_data):
    counts = []
    for doc_id, (server_transformed_elements, client_elements_server) in server_data.items():
        # Client exponentiates server's transformed elements (their own elements from the beginning) with their inverse secret and hashes them
        client_secret_inverse = pow(client_secret, -1, q)
        server_elements_client = []
        for elem in client_elements_server:
            transformed_elem = pow(elem, client_secret_inverse, P)
            elem_hash = blake2b((str(doc_id) + '||' + str(transformed_elem)).encode(), digest_size=64).hexdigest()
            server_elements_client.append(elem_hash)
        # Client computes the intersection
        set_client = set(server_transformed_elements)
        set_server = set(server_elements_client)
        intersection = set_client.intersection(set_server)
        count = len(intersection)
        counts.append((doc_id, count))
    return counts

if __name__ == "__main__":
    server_elements = server_setup()
    client_elements = client_setup()

    # Client's initial transformation
    client_secret, client_transformed_elements = client_transform(client_elements)

    """Client sends client_transformed_elements to server"""

    # Server's processing
    server_data = server_process(server_elements, client_transformed_elements)

    """Server sends server_transformed_elements and client_elements_server to client"""

    # Client computes intersections
    counts = client_compute_intersection(client_secret, server_data)
    for doc_id, count in counts:
        print(f"Document '{doc_id}' has {count} matching keyword(s).")