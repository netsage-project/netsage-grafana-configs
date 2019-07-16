# Developing the NetSage Grafana Configuration

This documents describes a number of practices related to developing the code in this repository. Specifically it covers:

 * Versioning
 * Branching
 * Releasing
 
## Versioning 

### Types of Releases

  * *Major Releases* - These are drastic changes that fundamentally change the software and user-experience. These likely only happen every few years at most. 
  * *Minor Releases* - These are releases that add major new functionality and can significantly change the user experience (hopefully for the better).
  * *Patch Releases* - These contain changes that improve the stability of the software and do not contain any new features.

### Numbering 

The NetSage version numbers are based on [semantic versioning](http://semver.org). Given the types of releases listed in the previous section, we need to capture the following information in our versioning scheme:

* **Major version** - This indicates to which *paradigm-shifting release* the software belongs. This will be a number starting at 1.
* **Minor version** - This indicates to which *major feature enhancement release* the software belongs. This will be a number starting at 0 for each new *major version*.
* **Patch version** - This indicates to which *bug fix release* the software belongs. This will be a number starting at 0 for each new *minor version*.

 
The primary goal of this scheme is to facilitate development on multiple software versions simultaneously without adding too much overhead for developers. We aim to accomplish this goal with the following:

 * A clearly defined branching strategy that cleanly separates code from different versions to prevent the accidental "leaking" of features and incompatible code
 * A set of tools for automating much of the process to reduce developer overhead and ensure the defined procedures are followed

This document will look at the high-level branching strategy, how to make a change to the code and how to implement the strategy when performing releases. 

## Branching 

### Basics
The following are the basic tenants of the branching strategy.

 * Each release version currently under development has a dedicated branch named using the version number (e.g. 1.0.0, 1.0.1, 1.1.0). These branches will be referred to as **release branches**.
 * Any changes that need to be made will be performed in a separate branch created from one of the release branches and named for the issue or feature being implemented (e.g. trello-1234). These will be referred to as **feature branches**
 * When it is time for release, the release branch will be merged into master and any later release branches. Master will be tagged and the release branch will be closed. No further changes should be made to the closed release branch. A new release branch will be created for the next version and the process will repeat.

### Naming Conventions
The following naming conventions should be followed when naming **branches**:

* **Release Branches** - Named using the version they represent in the form of `MAJOR.MINOR.PATCH`. All three parts MUST be included. Examples: *1.1.0*, *1.2.1*, *2.0.0*
* **Feature Branches** - Feature branches should be named for the trello issue they represent. Examples: *trello-1*, *trello-2*

The following naming conventions should be used when creating **tags** on master:

* **Release Tags** - When a release branch is merged into master, the commit of the merger should be tagged with the letter "v" followed by the version number. The "v" is added to prevent conflicts that can occur when tags and branches have the same name in git. Examples: *v1.1.0*, *v1.2.1*, *v2.0.0*

## Making a Change
All of the above can seem like a lot, but in practice it shouldn't be too difficult for a developer making changes to the code. The following are generally the steps for making a change:

1. Create an issue for the change you wish to make if it does not already exist.
1. Identify the earliest release for which the change needs to be applied. This information should be in the issue. If it is not, you may want to consult with the development team. Alternatively, a good rule of thumb is to apply it to the latest open release branch since the team is generally less conservative about changes going into later releases. 
1. Checkout the source code of the component that needs a change and create a new branch from the target version of the code. Examples commands are below where the target version is  X.Y.Z and trello ticket number is 1:
    ```
    git clone https://github.com/netsage-project/netsage-grafana-configs
    cd netsage-grafana-configs
    git fetch
    git checkout X.Y.Z
    git checkout -b trello-1
    git push origin trello-1
    ```
1. Make changes to your new branch
1. Check if the target version has had any changes since you began working on your change. If it has run `git merge X.Y.Z` on your feature branch. This helps avoid conflicts at pull request time. 
1. Submit a pull request to merge your change back into the target version.

From there your pull requests can be reviewed by the development team and merged back into the code.

## Handling Community Pull Requests

It is unreasonable to assume a community member that is not part of the day-to-day development team submitting a pull request will have intimate knowledge of our branching strategy or which version their change applies. The good news is that they do not have to have that knowledge and GitHub provides tools to get changes directed in the right place. 

It seems likely that most pull requests from the community at large will be based off of master since that will be the latest released code. It also seems likely that pull requests may try to merge into master, which we never want. Luckily GitHub allows maintainers of the project to change the target branch of a pull request by selecting **Edit** next the pull request title and then selecting the target branch from the pulldown. If the change will not merge into the desired branch, the reviewer should share that feedback with the community member.

In summary, community generated pull requests should be merged in the same as any other pull requests, but the reviewer may need to pay extra attention to the target branch and adjust it accordingly on behalf of the submitter.

## When to Merge

The process clearly defines that a branch is merged into both master and future release branches at release time. It is also highly recommended that future release branches periodically merge in changes from earlier open release branches to help catch conflicts early. Failure to do so can lead to surprises at release time including source code conflicts or bugs. No timetable is explicitly defined, but in general it seems good practice to never go more than a week without merging in changes from earlier releases while both are under active development.

## Releasing

A script is provided to do all the branching functions releated to a release. It is probably easiest to run the scripts from the VM environment described in the Vagrantfile provided with this repo. To initialize that environment run the following:

```
cd /path/to/repo/netsage-grafana-configs
vagrant up
vagrant ssh
```

The last command will log you into the VM. You should then add your git credentials to the VM such as adding your keys or creating a `~/.netrc` file.

When you are ready for a final release run the following replacing 1.0.0 with the version you are releasing:

```
/vagrant/scripts/release 1.0.0
```

The script will walk through all the repositories and do the following:

1. Checkout a clean copy of the target version branch from git
1. Merges the branch forward to next patch (e.g. 1.0.1) and minor (e.g. 1.1.0) release. It will create these branches if they do not already exist.
1. Merges the version branch into master
1. Tags master with vVERSION (e.g. v1.0.0)
1. Closes the version branch. This adds a file to the version branch that says no changes should be committed. This is used by some of the scripts in case you accidentally try to release a closed branch.
