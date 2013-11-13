import flask
from flask.ext.principal import (Principal, Permission, Identity,
                                 RoleNeed, UserNeed, PermissionDenied)

auth = flask.Blueprint('auth', __name__)

principals = Principal(use_sessions=False)


class need(object):
    """ A list of needs defined by our application. """

    everybody = RoleNeed('everybody')
    admin = RoleNeed('admin')
    authenticated = RoleNeed('authenticated')
    impossible = RoleNeed('impossible')

    @staticmethod
    def user_id(user_id):
        return UserNeed(user_id)

    @staticmethod
    def role(role):
        return RoleNeed(role)


admin_permission = Permission(need.admin)
impossible_permission = Permission(need.impossible)


def user_permission(user_id):
    return Permission(UserNeed(user_id))


def require(permission):
    def decorator(func):
        return permission.require()(func)
    return decorator


@auth.record
def register_principals(state):
    app = state.app
    principals.init_app(app)


@auth.app_context_processor
def inject_permissions():
    return {
        'admin_permission': admin_permission,
    }


@auth.route('/auth_debug', methods=['GET', 'POST'])
def debug():
    if not flask.current_app.config.get('AUTH_DEBUG'):
        flask.abort(404)

    if flask.request.method == 'POST':
        user_id = flask.request.form['user_id']
        roles = flask.request.form['roles'].strip().split()
        set_session_auth(user_id, roles)
        return flask.redirect(flask.url_for('.debug'))

    roles = flask.session.get('auth', {}).get('roles', [])
    return flask.render_template('auth/debug.html', **{
        'user_id': flask.g.identity.id,
        'roles_txt': ''.join('%s\n' % r for r in roles),
        'roles_example': (
            'admin\n'
            'expert:species:M\n'
            'expert:species:M:1353\n'
            'reviewer:habitat:8230\n'
        ),
    })


def set_session_auth(user_id=None, roles=[]):
    flask.session['auth'] = {'user_id': user_id, 'roles': roles}


@auth.before_app_request
def load_debug_auth():
    if not flask.current_app.config.get('AUTH_DEBUG'):
        return

    auth_data = flask.session.get('auth')
    if auth_data and auth_data.get('user_id'):
        identity = Identity(id=auth_data['user_id'],
                            auth_type='session')
        principals.set_identity(identity)

        identity.provides.add(need.user_id(identity.id))
        identity.provides.add(need.authenticated)
        for role_name in auth_data.get('roles', []):
            identity.provides.add(RoleNeed(role_name))

    if 'identity' in flask.g:
        flask.g.identity.provides.add(need.everybody)


@auth.app_errorhandler(PermissionDenied)
def handle_permission_denied(error):
    return flask.render_template('auth/denied.html')
