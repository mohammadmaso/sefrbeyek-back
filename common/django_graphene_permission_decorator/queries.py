from graphql import GraphQLError


def allow_authenticated(resolve):
    def wrapper(root, info, *args, **kwargs):
        if info.context.user.is_authenticated:
            return resolve(root, info, *args, **kwargs)
        else:
            raise GraphQLError('You must be logged in', extensions={
                               'code': "UNAUTHENTICATED"})

    return wrapper


def allow_superuser(resolve):
    def wrapper(root, info, *args, **kwargs):
        if info.context.user.is_authenticated:
            return resolve(root, info, *args, **kwargs)
        else:
            raise GraphQLError('User must be superuser.')

    return wrapper


def allow_staff(resolve):
    def wrapper(root, info, *args, **kwargs):
        if info.context.user.is_authenticated:
            return resolve(root, info, *args, **kwargs)
        else:
            raise GraphQLError('User must be staff.')

    return wrapper
