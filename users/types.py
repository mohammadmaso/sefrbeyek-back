import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphene import relay



class UserType(DjangoObjectType):

    def resolve_avatar(self, info):
        """Resolve avatar image absolute path"""
        if self.avatar:
            self.avatar = info.context.build_absolute_uri(self.avatar.url)
        return self.avatar

    class Meta:
        model = get_user_model()
        interfaces = (relay.Node, )
        exclude = ['password', 'verified', 'accepted_terms']

