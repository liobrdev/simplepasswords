from cryptocode import encrypt

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, CharField, RegexField

from entries.models import Entry


class ListEntrySerializer(ModelSerializer):
    class Meta:
        model = Entry
        fields = ['slug', 'title', 'created_at']
        read_only_fields = ['slug', 'title', 'created_at']


class EntrySerializer(ModelSerializer):
    slug = RegexField(r'^[\w-]{10}$', read_only=True)
    password = CharField(trim_whitespace=False, write_only=True, required=True)

    class Meta:
        model = Entry
        fields = ['slug', 'title', 'value', 'password', 'created_at']
        read_only_fields = ['slug', 'created_at']
    
    def validate_password(self, password):
        request = self.context['request']
        user = request.user
        if user.check_password(password):
            return password
        raise ValidationError('Invalid password.')

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        password = validated_data.pop('password')
        validated_data['value'] = encrypt(validated_data['value'], password)
        return Entry.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        value = validated_data.pop('value')
        password = validated_data.pop('password')
        instance.value = encrypt(value, password)
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        instance.value = value
        return instance