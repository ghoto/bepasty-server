# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

"""
Set metadata keys to specific values
"""

import errno

from flask import current_app, redirect, url_for, render_template, abort
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from . import blueprint
from ..utils.permissions import *


class SetKeyValueView(MethodView):
    # overwrite these in subclasses:
    REQUIRED_PERMISSION = None
    KEY = None
    NEXT_VALUE = None

    def get(self, name):
        if self.REQUIRED_PERMISSION is not None and not may(self.REQUIRED_PERMISSION):
            abort(403)
        try:
            with current_app.storage.openwrite(name) as item:
                if item.meta[self.KEY] == self.NEXT_VALUE:
                    error = '%s already is %r.' % (self.KEY, self.NEXT_VALUE)
                elif not item.meta['complete']:
                    error = 'Upload incomplete. Try again later.'
                else:
                    error = None
                if error:
                    return render_template('error.html', heading=item.meta['filename'], body=error), 409
                item.meta[self.KEY] = self.NEXT_VALUE
            return redirect(url_for('bepasty.display', name=name))

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                abort(404)
            raise


class LockView(SetKeyValueView):
    REQUIRED_PERMISSION = ADMIN
    KEY = 'locked'
    NEXT_VALUE = True


class UnlockView(SetKeyValueView):
    REQUIRED_PERMISSION = ADMIN
    KEY = 'locked'
    NEXT_VALUE = False


blueprint.add_url_rule('/<itemname:name>/+lock', view_func=LockView.as_view('lock'))
blueprint.add_url_rule('/<itemname:name>/+unlock', view_func=UnlockView.as_view('unlock'))