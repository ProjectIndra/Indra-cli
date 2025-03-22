from python_wireguard import Key


def generate_keys():
	private, public = Key.key_pair()
	return private,public

def store_keys(private_key, public_key, path):
	with open(path + "private.key", "w") as pk:
		pk.write(str(private_key))
	with open(path + "public.key", "w") as pub:
		pub.write(str(public_key))


if __name__ == "__main__":
	path="./"
	pri, pub = generate_keys()
	store_keys(pri, pub, path)
	# create client interface
	# vm peer setup

