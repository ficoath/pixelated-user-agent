#
# Copyright (c) 2014 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
from common import *


def click_first_element_with_class(context, classname):
    element = find_element_by_class_name(context, classname)
    element.click()


def is_side_nav_expanded(context):
    e = find_element_by_class_name(context, 'content')
    return u'move-right' in e.get_attribute("class")


def expand_side_nav(context):
    if is_side_nav_expanded(context):
        return

    toggle = find_element_by_class_name(context, 'side-nav-toggle')
    toggle.click()


@when('I select the tag \'{tag}\'')
def impl(context, tag):
    wait_for_user_alert_to_disapear(context)
    expand_side_nav(context)

    # try this multiple times as there are some race conditions
    try_again = 2
    success = False
    while (not success) and (try_again > 0):
        try:
            wait_until_element_is_visible_by_locator(context, (By.ID, 'tag-%s' % tag), timeout=20)

            e = find_element_by_id(context, 'tag-%s' % tag)
            e.click()

            wait_until_element_is_visible_by_locator(context, (By.CSS_SELECTOR, ".mail-list-entry__item[href*='%s']" % tag), timeout=20)
            success = True
        except TimeoutException:
            pass
        finally:
            try_again -= 1

    assert success


@when('I am in  \'{tag}\'')
def impl(context, tag):
    expand_side_nav(context)

    wait_until_element_is_visible_by_locator(context, (By.ID, 'tag-%s' % tag), 20)
    e = find_element_by_id(context, 'tag-%s' % tag)
    assert "selected" in e.get_attribute("class")
