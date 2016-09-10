# `homu-on-heroku`

> How to deploy a [Homu] instance to [Heroku]

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

~~**WARNING** This document doesn't cover how to use Homu or explain Homu terminology like "r+"
because that's covered by the [homu.io] website.~~ Actually, I'm going to cover a little on how Homu
works because there's not much documentation on some features. See the [operational notes] section.

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

- Deploy the Heroku app that resides in this repository by clicking the button below. Go with the
default values for pretty much everything, but feel free to set a name for the Heroku app.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Your Heroku app will crash right after deploying it because we haven't set right values for the
credentials -- we'll do that in a bit.

From this point, I'll refer to the name of your Heroku app as `$HEROKU_APP`.

### Under the `$HOMU_BOT` account

Login with your `$HOMU_BOT` account and perform these steps:

- [Create an Oauth application][0] with these parameters:
  - Application name: homu
  - Application description: (leave empty)
  - Homepage URL: `https://$HEROKU_APP.herokuapp.com`
  - Authorization callback URL: `http://$HEROKU_APP.herokuapp.com/callback`
  
**NOTE** the only field that matters is the callback URL, you can fill the other fields with whatever
you want.
  
[0]: https://github.com/settings/applications/new

- Define some config variables in your Heroku App.
  - Go to https://dashboard.heroku.com/apps/$HEROKU_APP/settings
  - Under the "Config variables" section, update these values:
    - `GH_OAUTH_ID`: Enter the "Client ID" value of the [Oauth application][1] you created in the
    previous step.
    - `GH_OAUTH_SECRET`: Enter the "Client Secret" of the [Oauth application][1] you created in the
    previous step.
    
[1]: https://github.com/settings/developers

- [Create a Personal Token Account][2] with "repo" and "user" scopes enabled. Use this token as the
`GH_ACCESS_TOKEN` config variable of your Heroku app.

[2]: https://github.com/settings/tokens/new

### Under your main GitHub account

Login with your main GitHub account, the one that owns the repositories you want use Homu with, and
perform these steps.

- Head to https://travis-ci.org/profile/info and copy the token listed there into your Heroku app
`TRAVIS_TOKEN` config variable.

- Tell Homu who has r+ rights.
  - Your Heroku app `HOMU_REVIEWERS` config variable is a space separated list of GitHub users that
  have r+ rights over *all* the repositories (see [Limitations]) Homu is gatekeeping. For example,
  set it to "moe larry curly", but without the double quotes, if those three users have r+ rights.

- (Optional) Generate a pair of SSH keys, associate them with GitHub and give Homu your private key.
This lets Homu use git locally which speeds up Travis by reducing temporary commits.
  - Generate a pair of SSH keys with e.g. `ssh-keygen -t rsa -b 4096 -C "for homu"`.
  - Associate the public key with [your GitHub account].
  - Copy the private key into your Heroku app `GIT_SSH_KEY` config variable.

[your GitHub account]: https://github.com/settings/keys

## Per repository setup

For each repository you want to use with Homu, perform these steps. I'll use the `$OWNER/$REPO`
"slug" to refer to a repository that has URL: https://github.com/$OWNER/$REPO.

- Append this repository to the list of repositories Homu is watching.

Currently, homu keeps two list of repos. Each list is stored as a config variable whose format is a
space-separated list of repo slugs e.g. "japaric/homu-on-heroku rust-lang/rust". The config var
`HOMU_TRAVIS_REPOS` lists the repos that must always pass Travis CI and `HOMU_APPVEYOR_REPOS` lists
the repos that must always pass AppVeyor CI. If a repository must pass both AppVeyor and Travis then
it must appear in both lists.

After updating these variables to not be empty, your Heroku app should get to the point where it
doesn't crash and it should render its dashboard. Head to `https://$HEROKU_APP.herokuapp.com` to
confirm.

- Go to https://github.com/$OWNER/$REPO/settings/collaboration and add `$HOMU_BOT` as a
collaborator.

- Add a webhook to your repository: Go to https://github.com/$OWNER/$REPO/settings/hooks/new and
fill the fields with:
  - Payload URL: `https://$HEROKU_APP.herokuapp.com/github`
  - Content type: application/json
  - Secret: (the value of your Heroku app `GH_WEBHOOK_SECRET` config variable)
  - Events: (pick 'let me select individual events' and choose Issue comment, Pull request, Push and
    **Status**)
  
After you create the webhook, GitHub will send a test payload to test your service. This test should
succeed at this point. If not check your Heroku app logs for clues about what went wrong.
  
- **Append** these two key-value pairs to your repository `.travis.yml`:

```
branches:
    only:
        # Only needed if you are already using branches.only.
        - auto

notifications:
    webhooks: https://$HEROKU_APP.herokuapp.com/travis
```

If you are going to use the "try" feature you'll also need to add the try branch to the
branches.only list. Again, this is only necessary if you are already using the branches.only list.

That's it! Homu is now gatekeeping this repository. You should now be able to r+ pull requests.

## Limitations

The Heroku app in its current form has a few limitations, but depending on your use case these may
not matter to you. The limitations are listed below:

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

## Updating your Heroku app

In the future, I might update the Heroku app in this repository and you may want to update your
deployed Heroku app to use a new release. You can do that with the following commands:

**NOTE** To run these commands, you'll need to have the [Heroku toolbelt] installed. Alternatively,
you can use [this Docker image] that comes with a pre-installed Heroku toolbelt.

[Heroku toolbelt]: https://toolbelt.heroku.com/
[this Docker image]: https://hub.docker.com/r/japaric/heroku/

```
$ heroku login
$ git clone https://github.com/japaric/homu-on-heroku
$ cd homu-on-heroku
$ git remote add heroku https://git.heroku.com/$HEROKU_APP.git
$ git push heroku master
```

## Operational notes

[operational notes]: #operational-notes

### What does the synchronize button do?

When you configure your repository to work with Homu for the first time, Homu doesn't know about the
**existing** PRs opened against your repo -- that's why the Homu queue for your repository is empty.
The synchronize button makes Homu go through your opened PRs and adds them to the queue.

**WARNING** The synchronize button on queue/all is known to not work. You'll get an internal server
error.

**NOTE** You don't need to click the synchronize button to make Homu learn about **new** PRs because
Homu will do that automatically.

Another scenario where you might need to use it is when new PRs are sent against your repo while
Homu was sleeping (if you are running it on a free dyno).

### Homu is not listening to my commands

Homu only listen to commands on PRs that appear on your repository queue. If your PR doesn't appear
on the queue you probably need to use the synchronize button.

### Homu got stuck testing a PR

This might happen if Homu was sleeping when the Travis test finished. The PR will appear as
"pending" in queue even though the Travis build finished. One way to unstuck Homu is to push a new
commit to the PR or force push an amendment to the HEAD commit without any change.

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
