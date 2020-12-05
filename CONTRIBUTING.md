# How to contribute

The help of the community is essential for projects like this. Users have 
different requirements and perspectives how their instances should work.

## Getting Started

Create a Feature request with a short but understandable description what the 
feature should look like and how the user can use it.

## Making Changes

* Create a topic branch from where you want to base your work.
  * This is usually the `development` branch.
  * Only target `release` branches if you are certain your fix must be on that
    branch.
* Make commits of logical and atomic units.
* Check for unnecessary whitespace with `git diff --check` before committing.
* Make sure your commit messages are in the proper format. Start the first 
  line of the commit with the issue number in parentheses.

## Development

To pass the official guidelines, all unit tests have to pass.
```shell
tox
```

