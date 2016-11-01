from jinja2 import Template
from homu.main import main
from homu import utils

import os
import sys

with open('cfg.template.toml') as f:
    template = Template(f.read())

ssh_key = os.environ.get('GIT_SSH_KEY', '')
admin_secret = os.environ.get('HOMU_WEB_SECRET', '')

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
    'web': {
        'port': os.environ['PORT'],
        'secret': admin_secret if admin_secret else 'false'
    },
}

with open('cfg.toml', 'w') as f:
    f.write(template.render(homu=homu))

os.makedirs(os.path.join(os.path.expanduser('~'), '.ssh'), exist_ok=True)

if os.path.isfile(os.path.expanduser('~/.ssh/known_hosts')):
    # grep exits 0 (which becomes false) if it finds the pattern
    github_unknown = bool(os.system('grep "^github.com " ~/.ssh/known_hosts > /dev/null'))
if github_unknown:
    utils.logged_call(['sh', '-c',
                       'ssh-keyscan github.com >> ~/.ssh/known_hosts'])

sys.exit(main())
