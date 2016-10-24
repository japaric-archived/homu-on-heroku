# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Operational notes to the README. Explanations of some undocumented Homu features/behaviors.
- Script to sync all repos' PR status from GitHub via Heroku scheduler
- Allow any of the CI repo lists to be blank.

## [v0.2.1]

### Added

- You can now use Homu "local_git" feature which speeds up Travis builds by reducing the number of
temporary commits.

## [v0.2.0] - 2016-04-29

### Added

- Add CHANGELOG.md.
- README: Add instructions on how to update a deployed Heroku app.

### Changed

- Use full "repo slug" (e.g. rust-lang/rust) instead of just the repo name (e.g. rust) to identify
each repository. This lets Homu monitor repositories from different owners but that share the same
name (e.g. rust-lang/rust and forked/rust).

## [v0.1.1] - 2016-04-29

### Fixed

- You can now register repositories that contain dots ('.') in their name.

## v0.1.0 - 2016-04-29

- Initial release

[Unreleased]: https://github.com/japaric/homu-on-heroku/compare/v0.2.1...HEAD
[v0.2.1]: https://github.com/japaric/homu-on-heroku/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/japaric/homu-on-heroku/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/japaric/homu-on-heroku/compare/v0.1.0...v0.1.1
