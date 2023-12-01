from django.contrib.auth import get_user_model
import graphene
from graphene import relay
from graphene_django.filter.fields import DjangoFilterConnectionField
from graphql_auth.schema import MeQuery
from graphql import GraphQLError

from common.django_graphene_permission_decorator.queries import allow_authenticated
from .types import (
    UserType,
)
from graphql_relay import from_global_id


class MeUserQuery(MeQuery):

    @allow_authenticated
    def resolve_me(self, info):
        return info.context.user

    me = graphene.Field(UserType)


class UserQuery(graphene.ObjectType):
    user = graphene.Field(UserType, username=graphene.String(required=True))
    all_users = DjangoFilterConnectionField(UserType)

    def resolve_user(parent, info, username):
        user = get_user_model().objects.filter(username=username)
        if user.exists():
            return user[0]
        else:
            raise GraphQLError('User not found.')


class Query(UserQuery, MeUserQuery, graphene.ObjectType):
    pass