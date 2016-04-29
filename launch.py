from jinja2 import Template
from homu.main import main

import os
import sys

with open('cfg.template.toml') as f:
    template = Template(f.read())

ssh_key = os.environ.get('GIT_SSH_KEY', '')

if ssh_key:
    local_git = "true"
else:
    local_git = "false"

repos = map(lambda slug: slug.split('/'), os.environ['HOMU_REPOS'].split(' '))

homu = {
    'gh': {
        'access_token': os.environ['GH_ACCESS_TOKEN'],
        'oauth_id': os.environ['GH_OAUTH_ID'],
        'oauth_secret': os.environ['GH_OAUTH_SECRET'],
        'webhook_secret': os.environ['GH_WEBHOOK_SECRET'],
    },
    'git': {
        'local_git': 'true' if ssh_key else 'false',
        'ssh_key': ssh_key,
    },
    'repos': repos,
    'reviewers': os.environ['HOMU_REVIEWERS'].split(' '),
    'travis': {
        'token': os.environ['TRAVIS_TOKEN']
    },
    'web': {
        'port': os.environ['PORT'],
    },
}

with open('cfg.toml', 'w') as f:
    f.write(template.render(homu=homu))

sys.exit(main())
