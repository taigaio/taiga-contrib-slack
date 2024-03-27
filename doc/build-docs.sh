#!/bin/sh

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos INC

make || exit 1
rm -rf /tmp/taiga-contrib-slack-doc-dist || exit 1
cp -r dist /tmp/taiga-contrib-slack-doc-dist || exit 1
git checkout gh-pages || exit 1
rm -rf dist || exit 1
mv /tmp/taiga-contrib-slack-doc-dist ../dist || exit 1
git add --all ../dist || exit 1
git commit -a -m "Update doc" || exit 1
