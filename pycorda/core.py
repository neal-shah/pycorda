import pandas as pd
import jaydebeapi as jdbc
import requests
import jks
import base64
import textwrap
import time
import re


class Node(object):
	"""
	Node object for connecting to a database and getting table dataframes

	Use get_tbname methods to get dataframe for table TBNAME. For example,
	calling node.get_vault_states() will return the dataframe for VAULT_STATES.
	After using the node, call the close() method to close the connection.
	"""

	# --- Notes regarding get methods ---
	# If table names will change often, it may be worth to
	# dynamically generate methods with some careful metaprogramming

	def __init__(self, url, username, password, path_to_jar='./db_driver.jar', node_root=None, web_server_url=None, name=''):
		"""
		Parameters
		----------
		url : str
			JDBC url to be connected
		username : str
			username of database user
		password : str
			password of database user
		path_to_jar : str
			path to database driver jar file
		"""

		self.set_name(name)

		driver_class = "org.{0}.Driver".format(re.findall(r":(.*):/", url)[0])

		self._conn = jdbc.connect(
			driver_class,
			url,
			[username, password],
			path_to_jar,
		)

		self._curs = self._conn.cursor()
		if node_root is not None:
			self.set_node_root(node_root)
		if web_server_url is not None:
			self.set_web_server_url(web_server_url)
	
	def set_name(self, name):
		self._name = name

	def send_api_request_get(self,api_url):
		if self._web_server_url is not None:
			request_url = self._web_server_url + api_url
			resp = requests.get(request_url)
			return resp.text
		else:
			return "No web_server set i.e. http://localhost:10007. Call set_web_server_url()"
	
	def set_web_server_url(self, web_server_url):
		self._web_server_url = web_server_url

	def set_node_root(self, node_root):
		self._node_root = node_root
		self._node_cert = node_root + '/certificates'
		self._node_cert_jks = self._node_cert + '/nodekeystore.jks'

	def display_keys_from_jks(self,password='cordacadevpass'):
		ks = jks.KeyStore.load(self._node_cert_jks,password)
		columns = ['ALIAS','PRIVATE_KEY']
		keys = pd.DataFrame([],columns=columns)
		for alias, pk in ks.private_keys.items():
			#keys = keys.append([[alias,pk.pkey_pkcs8,'PK']])
			df = pd.DataFrame([[alias,base64.b64encode(pk.pkey_pkcs8).decode('ascii')]],columns=columns)
			keys = keys.append(df,ignore_index=True)
		return keys

	def _get_df(self, table_name):
		"""Gets pandas dataframe from a table

		Parameters
		----------
		table_name : str
			name of table in database
		"""
		self._curs.execute("SELECT * FROM " + table_name)
		columns = [desc[0] for desc in self._curs.description] # column names
		return pd.DataFrame(self._curs.fetchall(), columns=columns)

	def get_node_attachments(self):
		return self._get_df("NODE_ATTACHMENTS")

	def get_node_attachments_contracts(self):
		return self._get_df("NODE_ATTACHMENTS_CONTRACTS")

	def get_node_checkpoints(self):
		return self._get_df("NODE_CHECKPOINTS")

	def get_node_contract_upgrades(self):
		return self._get_df("NODE_CONTRACT_UPGRADES")

	def get_node_indentities(self):
		return self._get_df("NODE_IDENTITIES")

	def get_node_infos(self):
		return self._get_df("NODE_INFOS")

	def get_node_info_hosts(self):
		return self._get_df("NODE_INFO_HOSTS")

	def get_node_info_party_cert(self):
		return self._get_df("NODE_INFO_PARTY_CERT")

	def get_node_link_nodeinfo_party(self):
		return self._get_df("NODE_LINK_NODEINFO_PARTY")

	def get_node_message_ids(self):
		return self._get_df("NODE_MESSAGE_IDS")

	def get_node_message_retry(self):
		return self._get_df("NODE_MESSAGE_RETRY")

	def get_node_named_identities(self):
		return self._get_df("NODE_NAMED_IDENTITIES")

	def get_node_our_key_pairs(self):
		return self._get_df("NODE_OUR_KEY_PAIRS")

	def get_node_properties(self):
		return self._get_df("NODE_PROPERTIES")

	def get_node_scheduled_states(self):
		return self._get_df("NODE_SCHEDULED_STATES")

	def get_node_transactions(self):
		return self._get_df("NODE_TRANSACTIONS")

	def get_node_transaction_mappings(self):
		return self._get_df("NODE_TRANSACTION_MAPPINGS")

	def get_vault_fungible_states(self):
		return self._get_df("VAULT_FUNGIBLE_STATES")

	def get_vault_fungible_states_parts(self):
		return self._get_df("VAULT_FUNGIBLE_STATES_PARTS")

	def get_vault_linear_states(self):
		return self._get_df("VAULT_LINEAR_STATES")

	def get_vault_linear_states_parts(self):
		return self._get_df("VAULT_LINEAR_STATES_PARTS")

	def get_vault_states(self):
		return self._get_df("VAULT_STATES")

	def get_vault_transaction_notes(self):
		return self._get_df("VAULT_TRANSACTION_NOTES")

	def get_state_party(self):
		return self._get_df("STATE_PARTY")

	def _snapshot_headers(self,header):
		return '\r\n\r\n -----------------  ' + header + ' \r\n'

	def find_transactions_by_linear_id(self,linear_id):
		linear_states = self.get_vault_linear_states()
		return linear_states[linear_states.UUID==linear_id]
	
	def find_vault_states_by_transaction_id(self,tx_id):
		vault_states = self.get_vault_states()
		return vault_states[vault_states.TRANSACTION_ID==tx_id]

	def find_vault_fungible_states_by_transaction_id(self,tx_id):
		vault_states = self.get_vault_fungible_states()
		return vault_states[vault_states.TRANSACTION_ID==tx_id]

	def find_vault_fungible_states_by_issuer(self,issuer):
		vault_states = self.get_vault_fungible_states()
		return vault_states[vault_states.ISSUER_NAME==issuer]

	def find_unconsumed_states_by_contract_state(self,contract_state_class_name):
		unconsumed_states = self.get_vault_states()
		return unconsumed_states[unconsumed_states.CONSUMED_TIMESTAMP.isnull()][unconsumed_states.CONTRACT_STATE_CLASS_NAME==contract_state_class_name]

	def find_linear_id_by_transaction_id(self,tx_id):
		linear_states = self.get_vault_linear_states()
		linear = linear_states[linear_states.TRANSACTION_ID==tx_id]
		return linear.iloc[0]['LINEAR_ID']

	def generate_snapshot(self,filename=None):
		if filename == None:
			filename = time.strftime(self._name+'-pycorda-snapshot-%Y%m%d-%H%M%S.log')
		f = open(filename,"w+")

		f.write(self._snapshot_headers('STATE_PARTY'))
		self.get_state_party().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_ATTACHMENT'))
		self.get_node_attachments().to_string(buf=f)

		f.write(self._snapshot_headers('NODE_ATTACHMENT_CONTRACTS'))
		self.get_node_attachments_contracts().to_string(buf=f)

		f.write(self._snapshot_headers('NODE_CHECKPOINTS'))
		self.get_node_checkpoints().to_string(buf=f)
	
		f.write(self._snapshot_headers('NODE_CONTRACT_UPGRADES'))
		self.get_node_contract_upgrades().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_IDENTITIES'))		
		self.get_node_indentities().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_INFOS'))
		self.get_node_infos().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_INFO_HOSTS'))
		self.get_node_info_hosts().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_INFO_PARTY_CERT'))
		self.get_node_info_party_cert().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_LINK_NODEINFO_PARTY'))
		self.get_node_link_nodeinfo_party().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_MESSAGE_IDS'))
		self.get_node_message_ids().to_string(buf=f)
		
		#f.write(self._snapshot_headers('NODE_IDENTITIES'))
		#self.get_node_message_retry()) - NEEDS TO BE REMOVED?
		
		f.write(self._snapshot_headers('NODE_NAMED_IDENTITIES'))
		self.get_node_named_identities().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_OUR_KEY_PAIRS'))
		self.get_node_our_key_pairs().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_PROPERTIES'))
		self.get_node_properties().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_SCHEDULED_STATES'))
		self.get_node_scheduled_states().to_string(buf=f)
		
		f.write(self._snapshot_headers('NODE_TRANSACTIONS'))
		self.get_node_transactions().to_string(buf=f)
		
		#f.write(self._snapshot_headers('NODE_IDENTITIES'))
		#self.get_node_transaction_mappings()) - ??

		f.write(self._snapshot_headers('VAULT_FUNGIBLE_STATES'))
		self.get_vault_fungible_states().to_string(buf=f)
		
		f.write(self._snapshot_headers('VAULT_FUNGIBLE_STATES_PARTS'))
		self.get_vault_fungible_states_parts().to_string(buf=f)
		
		f.write(self._snapshot_headers('VAULT_LINEAR_STATES'))
		self.get_vault_linear_states().to_string(buf=f)
		
		f.write(self._snapshot_headers('VAULT_LINEAR_STATES_PARTS'))
		self.get_vault_linear_states_parts().to_string(buf=f)
		
		f.write(self._snapshot_headers('VAULT_STATES'))
		self.get_vault_states().to_string(buf=f)
		
		f.write(self._snapshot_headers('VAULT_TRANSACTION_NOTES'))
		self.get_vault_transaction_notes().to_string(buf=f)

		f.close()

	def close(self):
		"""Closes the connection to the database"""
		self._curs.close()
		self._conn.close()


def print_pem(der_bytes, type):
	print("-----BEGIN %s-----" % type)
	print("\r\n".join(textwrap.wrap(base64.b64encode(der_bytes).decode('ascii'), 64)))
	print("-----END %s-----" % type)