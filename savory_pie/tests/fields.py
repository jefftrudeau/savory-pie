import unittest
from mock import Mock

from savory_pie.resources import ModelResource
from savory_pie.fields import PropertyField, FKPropertyField, SubModelResourceField


class PropertyFieldTest(unittest.TestCase):
    def test_simple_outgoing(self):
        source_object = Mock()
        source_object.foo = 20

        field = PropertyField(property='foo', type=int)

        target_dict = dict()

        field.handle_outgoing(source_object, target_dict)

        self.assertEqual(target_dict['foo'], 20)

    def test_simple_incoming(self):
        source_dict = {
            'foo': 20
        }

        field = PropertyField(property='foo', type=int)

        target_object = Mock()

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(target_object.foo, 20)

    def test_alternate_name_outgoing(self):
        source_object = Mock()
        source_object.foo = 20

        field = PropertyField(property='foo', type=int, json_property='bar')

        target_dict = dict()

        field.handle_outgoing(source_object, target_dict)

        self.assertEqual(target_dict['bar'], 20)

    def test_alternate_name_incoming(self):
        source_dict = {
            'bar': 20
        }

        field = PropertyField(property='foo', type=int, json_property='bar')

        target_object = Mock()

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(target_object.foo, 20)

    def test_automatic_json_naming(self):
        field = PropertyField(property='foo_bar', type=int)

        target_object = Mock()
        field.handle_incoming({'fooBar': 20}, target_object)

        self.assertEqual(target_object.foo_bar, 20)


class FKPropertyFieldTest(unittest.TestCase):
    def test_simple_outgoing(self):
        source_object = Mock()
        source_object.foo.bar = 20

        field = FKPropertyField(property='foo.bar', type=int)

        target_dict = dict()

        field.handle_outgoing(source_object, target_dict)

        self.assertEqual(target_dict['bar'], 20)

    def test_simple_incoming(self):
        source_dict = {
            'bar': 20
        }

        field = FKPropertyField(property='foo.bar', type=int)

        target_object = Mock()

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(target_object.foo.bar, 20)

    def test_alternate_name_outgoing(self):
        source_object = Mock()
        source_object.foo.bar = 20

        field = FKPropertyField(property='foo.bar', type=int, json_property='foo')

        target_dict = dict()

        field.handle_outgoing(source_object, target_dict)

        self.assertEqual(target_dict['foo'], 20)

    def test_alternate_name_incoming(self):
        source_dict = {
            'foo': 20
        }

        field = FKPropertyField(property='foo.bar', type=int, json_property='foo')

        target_object = Mock()

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(target_object.foo.bar, 20)

    def test_prepare(self):
        query_set = Mock()

        field = FKPropertyField(property='foo.bar.baz', type=int)

        result_query_set = field.prepare(query_set)

        query_set.select_related.assert_called_with('foo__bar')
        query_set_1 = query_set.select_related.return_value

        self.assertEqual(query_set_1, result_query_set)


class SubModelResourceFieldTest(unittest.TestCase):
    def test_simple_outgoing(self):
        source_object = Mock()
        source_object.foo.bar = 20

        class Resource(ModelResource):
            fields = [
                PropertyField(property='bar', type=int),
            ]
        field = SubModelResourceField(property='foo', resource_class=Resource)

        target_dict = dict()

        field.handle_outgoing(source_object, target_dict)

        self.assertEqual(target_dict['foo'], {'bar': 20})

    def test_simple_incoming(self):
        source_dict = {
            'foo': {'bar': 20},
        }

        class Resource(ModelResource):
            model_class = Mock()
            fields = [
                PropertyField(property='bar', type=int),
            ]
        field = SubModelResourceField(property='foo', resource_class=Resource)

        target_object = Mock()

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(20, target_object.foo.bar)
        target_object.foo.save.assert_called_with()

    def test_new_object_incoming(self):
        source_dict = {
            'foo': {'bar': 20},
        }

        class Resource(ModelResource):
            model_class = Mock()
            fields = [
                PropertyField(property='bar', type=int),
            ]
        field = SubModelResourceField(property='foo', resource_class=Resource)

        target_object = Mock()
        target_object.foo = None

        field.handle_incoming(source_dict, target_object)

        self.assertEqual(20, target_object.foo.bar)
        self.assertEqual(Resource.model_class.return_value, target_object.foo)
        target_object.foo.save.assert_called_with()
