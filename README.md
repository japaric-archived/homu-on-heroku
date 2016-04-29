# `homu-on-heroku`

> How-to: Deploy a [Homu] instance on [Heroku].

[Heroku]: https://www.heroku.com

Homu is a CI service that helps you enforce the "never break the build" policy in your GitHub
repositories (for more details about Homu check its [GitHub repository][Homu] and [homu.io]).

[Homu]: https://github.com/barosl/homu

[homu.io] is a Homu instance plus a front-end that lets you easily use Homu with your repositories.
However, right now homu.io is not accepting registration of new repositories, though its associated
[@homu] bot is still working non-stop on the repositories that were already registered.

[homu.io]: http://homu.io/
[@homu]: https://github.com/homu

Until [homu.io] "re-opens" its registration page, you can deploy your own Homu instance on a free
Heroku dyno and use it with all your repositories. The rest of this document will tell you how to do
that.

**WARNING** This document doesn't cover how to use Homu or explain Homu terminology like "r+"
because that's covered by the [homu.io] website.

## What you'll need

- An extra GitHub account that will become the Homu bot. For example, I'm using [@homunkulus]. I'll
refer to this (i.e. your) account as `$HOMU_BOT`.
- A Heroku account.

[@homunkulus]: https://github.com/homunkulus

## How to deploy

> Apologies, I didn't have time to make this procedure shorter/simpler.

The procedure consists of "two" parts: A series of "one-time" steps which you need to do once
(obviously), and a series of "per-repository" steps that need to be repeated for each repository you
want to use with Homu.

## One-time steps

### Deploy the Heroku app

- Deploy the Heroku app that resides in this repository by clicking the button below.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

From this point, I'll refer to the name of your Heroku app as `$HEROKU_APP`.

### Under the `$HOMU_BOT` account

Login with your `$HOMU_BOT` account and perform these steps:

- [Create an Oauth application][0] with these parameters:
  - Application name: Homu (but anything else will do)
  - Application description: <empty> (but anything will do)
  - Homepage URL: http://$HEROKU_APP.herokuapp.com
  - Authorization callback URL: http://$HEROKU_APP.herokuapp.com/callback
  
[0]: https://github.com/settings/applications/new

- Define some config variables in your Heroku App.
  - Go to https://dashboard.heroku.com/apps/$HEROKU_APP/settings
  - Under the "Config variables" section, update these values:
    - `GH_OAUTH_ID`: Enter the "Client ID" value of the [Oauth application][1] you created in the
    previous step.
    - `GH_OAUTH_SECRET`: Enter the "Client Secret" of the [Oauth application][1] you created in the
    previous step.
    
[1]: https://github.com/settings/applications

- [Create a Personal Token Account][2] with "repo" scope. Use this token as the `GH_ACCESS_TOKEN`
config variable in your Heroku app.

[2]: https://github.com/settings/tokens/new

### Under your main GitHub account

Login with your main GitHub account, the one that owns the repositories you want use Homu with, and
perform these steps.

- Head to https://travis-ci.org/profile/info and copy the token listed there into your Heroku app
`TRAVIS_TOKEN` config variable.

- Tell Homu who has r+ rights.
  - Your Heroku app `HOMU_REVIEWERS` config variable is a space separated list of GitHub users that
  have r+ rights over *all* the repositories (see [Limitations]) Homu is gatekeeping. For example,
  set it to "moe larry curly" if those three users have r+ rights.

## Per repository setup

For each repository you want to use with Homu, perform these steps. I'll use the `$OWNER/$REPO`
"slug" to refer to a repository that has URL: https://github.com/$OWNER/$REPO.

- Go to https://github.com/$OWNER/$REPO/settings/collaboration and add `$HOMU_BOT` as a
collaborator.

- Append this repository to the list of repositories Homu is watching
  - This list is stored in your Heroku app `HOMU_REPOS` config variable as a space-separated list.
  For example, the variable may look like this after updating it "added/last-time added/just-now",
  where "added" is the owner of the "last-time" and "just-now" repositories.

- Add a webhook to your repository: Go to https://github.com/$OWNER/$REPO/settings/hooks/new and
fill the fields with:
  - Payload URL: http://$HEROKU_APP.herokuapp.com/github
  - Content type: application/json
  - Secret: (the value of your Heroku app `GH_WEBHOOK_SECRET` config variable)
  - Events: (pick 'let me select individual events' and choose Issue comment, Pull request and Push)
  
After you create the webhook, GitHub will send a test payload to test your service. This test should
succeed at this point. If not check your Heroku app logs for clues about what went wrong.
  
- **Append** these two key-value pairs to your repository `.travis.yml`:

```
branches:
    only:
        - auto

webhooks: http://$HEROKU_APP.herokuapp.com/travis
```

That's it! Homu is now gatekeeping this repository. If you visit http://$HEROKU_APP.herokuapp.com
the repository you just configured should be listed over there and you should be able to r+ pull
requests.

## Limitations

[Limitations]: #limitations

- We use the same travis token for all the repos. This pretty much means that all the repos
that Homu watches over must be owned by the same GitHub user/organization.
- We use the same set of reviewers for all the repos.

Both issues can be fixed with config variables that override the "global" values on a per repository
basis. We just have to settle on a format for the variable name. Strawman format:

```
# Global values
HOMU_REVIEWERS="larry moe curly"
TRAVIS_TOKEN="deadbeef"

# Overrides
HOMU_REVIEWERS_FOR_${OWNER//-/_}_${REPO//-/_}="larry moe"
TRAVIS_TOKEN_FOR_${OWNER//-/_}_${REPO//-/_}="deadc0de"

# NOTE ${VAR//-/_} means $VAR but with the `-` replaced with `_`. Example: if VAR=the-three-stooges,
# then ${VAR//-/_} is "the_three_stooges"
```

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the
work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any
additional terms or conditions.
