# MS-PSI

import random
from hashlib import blake2b
from collections import Counter

# Large safe prime P (2048-bit prime from RFC 7919)
# Hex representation of the prime is used because Python struggles with large floating point number operations
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
    # Server's keyword sets
    server_documents = {
        'doc1': ['apple', 'banana', 'cherry', 'apple'],
        'doc2': ['banana', 'date', 'fig', 'banana'],
        'doc3': ['cherry', 'date', 'grape', 'date'],
        'doc4': ['apple', 'date', 'kiwi', 'date'],
        'doc5': ['banana', 'cherry', 'lemon', 'banana', 'cherry']
    }

    # Hash/encrypt server's keywords per document
    server_elements_per_doc = {doc_id: [hash_to_int(kwd) for kwd in keywords]
                                for doc_id, keywords in server_documents.items()}

    return server_elements_per_doc

def client_setup():
    # Client inputs the keywords they wish to search for
    user_input = input("Please enter keywords to search separated by spaces: ").strip()
    client_keywords = [word for word in user_input.split() if word]

    # Assign IDs to the keywords
    client_keyword_ids = list(range(1, len(client_keywords)+1))

    # Hash/encrypt client's keywords to integers and map them to IDs
    client_elements = []
    client_element_id_map = {}
    for idx, kwd in zip(client_keyword_ids, client_keywords):
        elem = hash_to_int(kwd)
        client_elements.append(elem)
        if elem not in client_element_id_map:
            client_element_id_map[elem] = []
        client_element_id_map[elem].append(idx)

    return client_elements, client_element_id_map

def client_transform(client_elements, client_element_id_map):
    # Client generates a secret and exponentiates their hashed elements
    client_secret = generate_secret()
    client_element_counts = Counter(client_elements)
    client_transformed_elements = {}
    for elem, count in client_element_counts.items():
        transformed_elem = pow(G, elem * client_secret, P)
        client_transformed_elements[transformed_elem] = {'count': count, 'ids': client_element_id_map[elem]}
    return client_secret, client_transformed_elements

def server_process(server_elements_per_doc, client_transformed_elements):
    # Server generates it's secret
    server_secret = generate_secret()
    server_data = {}
    for doc_id, server_elements in server_elements_per_doc.items():
        # Server creates its tags and tag collection, i.e. server exponentiates their hashed elements and hashes them again
        tag_collection = set()
        for elem in server_elements:
            tags = pow(G, elem * server_secret, P) # Here we create the tags t that are in t^(i), for all i
            elem_hash = blake2b((str(doc_id) + '||' + str(tags)).encode(), digest_size=64).hexdigest()
            tag_collection.add(elem_hash) # Tag collection TC (N ist stored implicitly due to server_data being a dictionary)

        # THIS IS STEP 4 (put me in a new func)
        # Server exponentiates client's elements with server's secret
        client_elements_server = {}
        for transformed_elem, value in client_transformed_elements.items():
            transformed_elem_server = pow(transformed_elem, server_secret, P)
            client_elements_server[transformed_elem_server] = value  # value includes 'count' and 'ids'

        server_data[doc_id] = (tag_collection, client_elements_server)
    return server_data

def client_compute_intersection(client_secret, server_data):
    counts_per_doc = []
    for doc_id, (tag_collection, client_elements_server) in server_data.items():
        # Client exponentiates server's transformed elements (their own elements from the beginning) with their inverse secret and hashes them
        client_secret_inverse = pow(client_secret, -1, q)
        server_elements_client = set()
        for elem, count in client_elements_server.items():
            transformed_elem = pow(elem, client_secret_inverse, P)
            elem_hash = blake2b((str(doc_id) + '||' + str(transformed_elem)).encode(), digest_size=64).hexdigest()

            # Client finds multiset intersection (considering multiplicities)
            if elem_hash in tag_collection:
                ids = count['ids']
                server_elements_client.update(ids)
        counts_per_doc.append((doc_id, server_elements_client))
    return counts_per_doc

if __name__ == "__main__":
    server_elements_per_doc = server_setup()
    client_elements, client_element_id_map = client_setup()

    # Client's initial transformation
    client_secret, client_transformed_elements = client_transform(client_elements, client_element_id_map)

    """Client sends client_transformed_elements to server"""

    # Server's processing
    server_data = server_process(server_elements_per_doc, client_transformed_elements)

    """Server sends tag_collection and client_elements_server to client"""

    # Client computes intersections
    counts_per_doc = client_compute_intersection(client_secret, server_data)
    for doc_id, ids in counts_per_doc:
        ids = sorted(ids)
        if ids:
            ids_str = ', '.join(map(str, ids))
            print(f"Document '{doc_id}' has matching keyword IDs: {ids_str}.")
        else:
            print(f"Document '{doc_id}' has no matching keywords.")