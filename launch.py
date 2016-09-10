from jinja2 import Template
from homu.main import main
from homu import utils

import os
import sys

with open('cfg.template.toml') as f:
    template = Template(f.read())

ssh_key = os.environ.get('GIT_SSH_KEY', '')

repos = {}

def append(slug, ci):
    if slug in repos:
        if ci == 'appveyor':
            repos[slug]['appveyor'] = True

        if ci == 'travis':
            repos[slug]['travis'] = True
    else:
        [owner, name] = slug.split('/')

        repos[slug] = {
            'appveyor': True if ci == 'appveyor' else False,
            'name': name,
            'owner': owner,
            'slug': slug,
            'travis': True if ci == 'travis' else False,
        }

for slug in os.environ['HOMU_APPVEYOR_REPOS'].split(' '):
    append(slug, 'appveyor')

for slug in os.environ['HOMU_TRAVIS_REPOS'].split(' '):
    append(slug, 'travis')

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
    'repos': repos.values(),
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

os.makedirs(os.path.join(os.path.expanduser('~'), '.ssh'))
utils.logged_call(['sh', '-c',
                   'ssh-keyscan -H github.com >> ~/.ssh/known_hosts'])

sys.exit(main())
