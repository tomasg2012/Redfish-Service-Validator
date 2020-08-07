
from bs4 import BeautifulSoup
import logging, sys
import glob, os
from commonRedfish import getType, getNamespace, getNamespaceUnversioned, getVersion, compareMinVersion, splitVersionString

my_logger = logging.getLogger(__name__)
my_logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
my_logger.addHandler(ch)

def check_redfish_extensions_alias(namespace, alias):
    """
    Check that edmx:Include for Namespace RedfishExtensions has the expected 'Redfish' Alias attribute
    :param name: the name of the resource
    :param item: the edmx:Include item for RedfishExtensions
    :return: bool
    """
    if alias is None or alias != 'Redfish':
        msg = ("In the metadata, the {} namespace must have an alias of 'Redfish'. The alias is {}. " +
               "This may cause properties of the form [PropertyName]@Redfish.TermName to be unrecognized.")
        my_logger.error(msg.format(namespace,
                             'missing' if alias is None else "'" + str(alias) + "'"))
        return False
    return True

class SchemaDefinition(object):
    def __init__(self, tag, parent_type):
        pass

class SchemaDocument(object):
    def __init__(self, data, name='unnamed document', origin=None):
        self.soup = BeautifulSoup(data, "xml")
        self.name = name
        self.origin = origin
        self.refs = None
        self.entities = self.gatherInformation('EntityType')
        self.refs = self.getReferenceDetails()

    def gatherInformation(self, tag):
        
        pass

    def getSchemaFromReference(self, namespace):
        """getSchemaFromReference

        Get SchemaObj from generated references

        :param namespace: Namespace of reference
        """
        tup = self.refs.get(namespace)
        if tup is None:
            tup = self.refs.get(getNamespace(namespace))
            if tup is None:
                my_logger.warning('No such reference {} in {}'.format(namespace, self.name))
            else:
                my_logger.warning('No such reference {} in {}, using unversioned'.format(namespace, self.name))
        return tup

    def getReferenceDetails(self, metadata=None):
        """
        Create a reference dictionary from a soup file

        param arg1: soup
        param metadata_dict: dictionary of service metadata, compare with
        return: dictionary
        """
        refDict = {}
    
        # if self.refs is not None:
        #     return self.refs

        maintag = self.soup.find("edmx:Edmx", recursive=False)
        reftags = maintag.find_all('edmx:Reference', recursive=False)
        for ref in reftags:
            includes = ref.find_all('edmx:Include', recursive=False)
            for item in includes:
                uri = ref.get('Uri')
                ns, alias = (item.get(x) for x in ['Namespace', 'Alias'])
                if ns is None or uri is None:
                    my_logger.error("Reference incorrect for: {}".format(item))
                    continue
                if alias is None:
                    alias = ns
                refDict[alias] = {'namespace': ns, 'uri': uri}
                # Check for proper Alias for RedfishExtensions
                if isinstance(self, MetadataDocument) and ns.startswith('RedfishExtensions.'):
                    check_bool = check_redfish_extensions_alias(ns, alias)

        cntref = len(refDict)
        if metadata is not None:
            refDict.update(metadata.getReferenceDetails())
        my_logger.debug("References generated from {}: {} out of {}".format(self.name, cntref, len(refDict)))
        return refDict

class MetadataDocument(SchemaDocument):
    def __init__(self, data):
        super().__init__(data, '$metadata')

class SchemaStore(object):
    def __init__(self, metadata_document, local_dir=None, prefer_local=True):
        self.available_schema = {}
        self.available_schema_files = {}
        self.cached_files = {}
        if metadata_document is not None:
            self.available_schema = metadata_document.getReferenceDetails()
        if local_dir is not None:
            my_local_schema = glob.glob(os.path.join(local_dir, '*'))
            for path in my_local_schema:
                x = path.rsplit('_v1', 1)[0] if '_v1' in path else path
                x = x.rsplit('.xml', 1)[0] if '.xml' in x else x
                self.available_schema_files[os.path.basename(x)] = {
                    'namespace': os.path.basename(x),
                    'uri': path 
                }
        self.trouble_message = {}

    def getSchema(self, type_name, prefer_local=True):
        my_namespace = getNamespace(type_name)
        my_schema = self.available_schema.get(my_namespace)
        if my_schema is None:
            my_schema = self.available_schema.get(getNamespaceUnversioned(type_name))
            # print error
            my_logger.error('Metadata does not contain relevant import name')
        if my_namespace in self.cached_files:
            return self.cached_files[my_namespace]
        my_local_schema = self.available_schema_files.get(getNamespaceUnversioned(type_name))
        if my_local_schema is not None and (prefer_local or my_schema is None):
            with open(my_local_schema['uri']) as f:
                my_file = SchemaDocument(f.read(), origin='local')
            return my_file
        elif my_schema is not None:
            return True
        else:
            return None
                

