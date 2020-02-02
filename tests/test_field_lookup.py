from django.db import models
from django.test import TestCase
from rest_framework import serializers

from drf_writable_nested import mixins


class LookupChild(models.Model):
    name = models.TextField()


class LookupParent(models.Model):
    child = models.ForeignKey(LookupChild, on_delete=models.CASCADE)


class LookupGrandParent(models.Model):
    child = models.ForeignKey(LookupParent, on_delete=models.CASCADE)


class LookupReverseChild(models.Model):
    name = models.TextField()
    parent = models.ForeignKey(LookupParent, on_delete=models.CASCADE, related_name='children')


class ChildSerializer(mixins.FieldLookupMixin, serializers.ModelSerializer):
    class Meta:
        model = LookupChild
        fields = '__all__'


class ReverseChildSerializer(mixins.FieldLookupMixin, serializers.ModelSerializer):
    class Meta:
        model = LookupReverseChild
        fields = '__all__'


class ParentSerializer(mixins.FieldLookupMixin, serializers.ModelSerializer):
    class Meta:
        model = LookupParent
        fields = '__all__'
    # source of a 1:many relationship
    child = ChildSerializer()
    children = ReverseChildSerializer(many=True)


class GrandParentSerializer(mixins.FieldLookupMixin, serializers.ModelSerializer):
    class Meta:
        model = LookupGrandParent
        fields = '__all__'
    # source of a 1:many relationship
    child = ParentSerializer()


class FieldTypesTest(TestCase):

    def test_field_types_grandparent(self):
        serializer = GrandParentSerializer()
        self.assertEqual(
            {
                'id': serializer.TYPE_READ_ONLY,
                'child': serializer.TYPE_DIRECT,
            },
            serializer.field_types
        )

    def test_field_types_parent(self):
        serializer = GrandParentSerializer()
        self.assertEqual(
            {
                'id': serializer.TYPE_READ_ONLY,
                'child': serializer.TYPE_DIRECT,
                'children': serializer.TYPE_REVERSE,
            },
            serializer.fields['child'].field_types
        )

    def test_field_types_child(self):
        serializer = GrandParentSerializer()
        self.assertEqual(
            {
                'id': serializer.TYPE_READ_ONLY,
                'name': serializer.TYPE_LOCAL,
            },
            serializer.fields['child'].fields['child'].field_types
        )

    def test_field_types_reversechild(self):
        serializer = GrandParentSerializer()
        self.assertEqual(
            {
                'id': serializer.TYPE_READ_ONLY,
                'name': serializer.TYPE_LOCAL,
                # must have a nested serializer to be "direct" otherwise it's just a local value
                'parent': serializer.TYPE_LOCAL,
            },
            serializer.fields['child'].fields['children'].child.field_types
        )


class GetModelFieldTest(TestCase):

    def test_reverse(self):
        serializer = ParentSerializer()
        model_field = serializer._get_model_field('children')
        print(type(model_field))
        # opposite side of a ForeignKey is a ManyToOne
        self.assertIsInstance(
            model_field,
            models.ManyToOneRel,
        )
