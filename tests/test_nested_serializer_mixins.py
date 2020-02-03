from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase, RequestFactory
from rest_framework import serializers

from drf_writable_nested import mixins


#####################
# Generic Serializer
#####################
class Child(models.Model):
    name = models.TextField()


class ChildGetOrCreateSerializer(mixins.GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    DEFAULT_MATCH_ON = ['name']

    class Meta:
        model = Child
        fields = '__all__'


class GenericParentRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.Serializer):
    class Meta:
        fields = '__all__'
    # source of a 1:many relationship
    child = ChildGetOrCreateSerializer()

    def create(self, validated_data):
        # "container only", no create logic
        return validated_data


##################
# Direct Relation
##################
class Parent(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)


class ParentMany(models.Model):
    children = models.ManyToManyField(Child)


class ParentRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
    # source of a 1:many relationship
    child = ChildGetOrCreateSerializer()


class ParentManyRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = ParentMany
        fields = '__all__'
    # source of a m2m relationship
    children = ChildGetOrCreateSerializer(many=True)


###################
# Reverse Relation
###################
class ReverseParent(models.Model):
    pass


class ReverseChild(models.Model):
    name = models.TextField()
    parent = models.ForeignKey(ReverseParent, on_delete=models.CASCADE, related_name='children')


class ReverseManyParent(models.Model):
    pass


class ReverseManyChild(models.Model):
    name = models.TextField()
    parent = models.ManyToManyField(ReverseManyParent, related_name='children')


class ReverseChildGetOrCreateSerializer(mixins.GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    DEFAULT_MATCH_ON = ['name']

    class Meta:
        model = ReverseChild
        fields = '__all__'


class ReverseManyChildGetOrCreateSerializer(mixins.GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    DEFAULT_MATCH_ON = ['name']

    class Meta:
        model = ReverseManyChild
        fields = '__all__'


class ReverseParentRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = ReverseParent
        fields = '__all__'
    # target of a 1:many relationship
    children = ReverseChildGetOrCreateSerializer(many=True)


class ReverseManyParentRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = ReverseManyParent
        fields = '__all__'
    # target of a m2m relationship
    children = ReverseManyChildGetOrCreateSerializer(many=True)


class WritableNestedModelSerializerTest(TestCase):

    def test_generic_nested_create(self):
        data = {
            "child": {
                "name": "test",
            }
        }

        serializer = GenericParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

    def test_generic_nested_get(self):
        """A second run with a GetOrCreate nested serializer should find same child object (by name)"""
        data = {
            "child": {
                "name": "test",
            }
        }

        serializer = GenericParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        serializer = GenericParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            1,
            Child.objects.count(),
        )

    def test_direct_nested_create(self):
        data = {
            "child": {
                "name": "test",
            }
        }

        serializer = ParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

    def test_direct_nested_get(self):
        """A second run with a GetOrCreate nested serializer should find same child object (by name)"""
        data = {
            "child": {
                "name": "test",
            }
        }

        serializer = ParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        serializer = ParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            2,
            Parent.objects.count()
        )

        self.assertEqual(
            1,
            Child.objects.count(),
        )

    def test_direct_many_nested_create(self):
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ParentManyRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

    def test_direct_many_nested_get(self):
        """A second run with a GetOrCreate nested serializer should find same child object (by name)"""
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ParentManyRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        serializer = ParentManyRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            1,
            Child.objects.count(),
        )

    def test_reverse_nested_create(self):
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ReverseParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

    def test_reverse_nested_get(self):
        """A second run with a GetOrCreate nested serializer should find same child object (by name)"""
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ReverseParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        serializer = ReverseParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            2,
            ReverseParent.objects.count()
        )

        self.assertEqual(
            1,
            ReverseChild.objects.count(),
        )

    def test_reverse_many_nested_create(self):
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ReverseManyParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

    def test_reverse_many_nested_get(self):
        """A second run with a GetOrCreate nested serializer should find same child object (by name)"""
        data = {
            "children": [{
                "name": "test",
            }]
        }

        serializer = ReverseManyParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        serializer = ReverseManyParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            1,
            ReverseManyChild.objects.count(),
        )


###################
# 3-Layer Relation
###################
class GrandParent(models.Model):
    child = models.ForeignKey(Parent, on_delete=models.CASCADE)


class NestedParentGetOrCreateSerializer(mixins.GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
    # source of a 1:many relationship
    child = ChildGetOrCreateSerializer()


class GrandParentRelatedSaveSerializer(mixins.RelatedSaveMixin, serializers.ModelSerializer):
    class Meta:
        model = GrandParent
        fields = '__all__'
    # source of a 1:many relationship
    child = NestedParentGetOrCreateSerializer()


class NestedWritableNestedModelSerializerTest(TestCase):

    def test_direct_nested_create(self):
        data = {
            "child": {
                "child": {
                    "name": "test",
                }
            }
        }

        serializer = GrandParentRelatedSaveSerializer(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            1,
            GrandParent.objects.count(),
        )

        self.assertEqual(
            1,
            Parent.objects.count(),
        )

        self.assertEqual(
            1,
            Child.objects.count(),
        )


##############
# Create Only
##############

class ChildCreateOnlySerializer(mixins.CreateOnlyNestedSerializerMixin, serializers.ModelSerializer):
    DEFAULT_MATCH_ON = ['name']

    class Meta:
        model = Child
        fields = '__all__'


class ParentRelatedSaveSerializerCreateOnly(mixins.RelatedSaveMixin, serializers.Serializer):
    class Meta:
        fields = '__all__'
    # source of a 1:many relationship
    child = ChildCreateOnlySerializer()

    def create(self, validated_data):
        # "container only", no create logic
        return validated_data


class CreateOnlyModelSerializerTest(TestCase):

    def test_create_despite_match(self):
        """Create Only serializers will not match an existing object (despite match_on)"""
        data = {
            "child": {
                "name": "test",
            }
        }

        serializer = ParentRelatedSaveSerializerCreateOnly(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            1,
            Child.objects.count()
        )

        serializer = ParentRelatedSaveSerializerCreateOnly(data=data)
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()

        self.assertEqual(
            2,
            Child.objects.count()
        )


#####################
# Context Conduction
#####################
class ContextChild(models.Model):
    name = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class ContextChildGetOrCreateSerializer(mixins.GetOrCreateNestedSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ContextChild
        fields = '__all__'
        extra_kwargs = {
            'owner': {
                'default': serializers.CurrentUserDefault(),
            }
        }


class GenericContextParentRelatedSaveSerializer(mixins.RelatedSaveMixin):
    child = ContextChildGetOrCreateSerializer()

    def create(self, validated_data):
        # "container only", no create logic
        return validated_data


class GenericContextGrandParentRelatedSaveSerializer(mixins.RelatedSaveMixin):
    child = GenericContextParentRelatedSaveSerializer()

    def create(self, validated_data):
        # "container only", no create logic
        return validated_data


class ContextConductionTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create(username="test_user")

    def test_context_conduction(self):
        data = {
            "child": {
                "child": {
                    "name": "test",
                }
            }
        }

        request = RequestFactory()
        request.user = self.user

        serializer = GenericContextGrandParentRelatedSaveSerializer(data=data)
        serializer._context = {
            'request': request
        }
        valid = serializer.is_valid()
        self.assertTrue(
            valid,
            "Serializer should have been valid:  {}".format(serializer.errors)
        )
        serializer.save()
