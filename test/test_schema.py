# Copyright Notice:
# Copyright 2017-2020 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Validator/blob/master/LICENSE.md
#
# Unit tests for RedfishServiceValidator.py
#

from unittest import TestCase
from unittest import mock
import datetime
import sys
import os

sys.path.append('../')

from SchemaObject import SchemaDocument, MetadataDocument, SchemaStore

class SchemaTest(TestCase):

    """
    Tests for functions setup_operation() and run_systems_operation()
    """
    def test_schema_doc(self):
        with open('./test/testdata/example_metadata.xml') as f:
            doc = MetadataDocument(f.read())
        my_refs = doc.getReferenceDetails()
        assert('ServiceRoot' in my_refs)
        assert(my_refs['ServiceRoot']['namespace'] == 'ServiceRoot')
        assert(my_refs['ServiceRoot']['uri'] == 'http://redfish.dmtf.org/schemas/v1/ServiceRoot_v1.xml')
        assert(my_refs['Redfish']['namespace'] == 'RedfishExtensions.v1_0_0')

        with open('./test/testdata/example_metadata_no_redfish.xml') as f:
            sub_doc = MetadataDocument(f.read())

        with open('./test/testdata/ServiceRoot_v1.xml') as f:
            sub_doc = SchemaDocument(f.read())

        my_refs = sub_doc.getReferenceDetails(metadata=doc)

    def test_schema_store(self):
        with open('./test/testdata/example_metadata.xml') as f:
            doc = MetadataDocument(f.read())
        my_store = SchemaStore(doc)
        assert(len(my_store.available_schema) > 0)
        assert(len(my_store.available_schema_files) == 0)
        assert(my_store.getSchema('ServiceRoot'))

    def test_schema_store_local(self):
        with open('./test/testdata/example_metadata.xml') as f:
            doc = MetadataDocument(f.read())
        my_store = SchemaStore(doc, os.path.join('test', 'testdata'))
        print(my_store.available_schema)
        print(my_store.available_schema_files)
        assert(my_store.getSchema('ServiceRoot'))
        assert(my_store.getSchema('ResourceObject') is None)

    def test_get_from_reference(self):
        with open('./test/testdata/example_metadata.xml') as f:
            doc = MetadataDocument(f.read())
        my_store = SchemaStore(doc, os.path.join('test', 'testdata'))
        my_schema = my_store.getSchema('ServiceRoot')
        assert(my_schema.getSchemaFromReference('Resource'))
        assert(my_schema.getSchemaFromReference('Resource.v1_0_0'))
        assert(my_schema.getSchemaFromReference('Resource'))
        assert(my_schema.getSchemaFromReference('Resource.v1_0_2'))
        assert(my_schema.getSchemaFromReference('ResourceObject') is None)



    def test_highest_type(self):
        pass

    def test_get_type_tag(self):
        pass

    def test_get_parent_type(self):
        pass






