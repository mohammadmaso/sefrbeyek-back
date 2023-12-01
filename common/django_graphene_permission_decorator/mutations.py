from graphql import GraphQLError


def allow_authenticated(mutation_function):
    def wrapper(cls, root, info, *args, **kwargs):
        if info.context.user.is_authenticated:
            return mutation_function(cls, root, info, *args, **kwargs)
        else:
            raise GraphQLError('You must be logged in', extensions={
                               'code': "UNAUTHENTICATED"})

    return wrapper


def allow_superuser(mutation_function):
    def wrapper(cls, root, info, *args, **kwargs):
        if info.context.user.is_superuser:
            return mutation_function(cls, root, info, *args, **kwargs)
        else:
            raise GraphQLError('User must be superuser.')

    return wrapper


def allow_staff(mutation_function):
    def wrapper(cls, root, info, *args, **kwargs):
        if info.context.user.is_staff:
            return mutation_function(cls, root, info, *args, **kwargs)
        else:
            raise GraphQLError('User must be staff.')

    return wrapper
