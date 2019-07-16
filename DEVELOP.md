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

* **Major version** - This indicates to which *major release* the software belongs. This will be a number starting at 1.
* **Minor version** - This indicates to which *minor feature enhancement release* the software belongs. This will be a number starting at 0 for each new *major version*.
* **Patch version** - This indicates to which *bug fix release* the software belongs. This will be a number starting at 0 for each new *minor version*. 

## Branching 

The primary goal of the branching scheme is to facilitate development on multiple software versions simultaneously without adding too much overhead for developers. We aim to accomplish this goal with the following:

 * A clearly defined branching strategy that cleanly separates code from different versions to prevent the accidental "leaking" of features and incompatible code
 * A set of tools for automating much of the process to reduce developer overhead and ensure the defined procedures are followed

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

### Making a Change
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

### Handling Community Pull Requests

It is unreasonable to assume a community member that is not part of the day-to-day development team submitting a pull request will have intimate knowledge of our branching strategy or which version their change applies. The good news is that they do not have to have that knowledge and GitHub provides tools to get changes directed in the right place. 

It seems likely that most pull requests from the community at large will be based off of master since that will be the latest released code. It also seems likely that pull requests may try to merge into master, which we never want. Luckily GitHub allows maintainers of the project to change the target branch of a pull request by selecting **Edit** next the pull request title and then selecting the target branch from the pulldown. If the change will not merge into the desired branch, the reviewer should share that feedback with the community member.

In summary, community generated pull requests should be merged in the same as any other pull requests, but the reviewer may need to pay extra attention to the target branch and adjust it accordingly on behalf of the submitter.

### When to Merge

The process clearly defines that a branch is merged into both master and future release branches at release time. It is also highly recommended that future release branches periodically merge in changes from earlier open release branches to help catch conflicts early. Failure to do so can lead to surprises at release time including source code conflicts or bugs. No timetable is explicitly defined, but in general it seems good practice to never go more than a week without merging in changes from earlier releases while both are under active development.

### Example Workflow

![Example Branching Workflow](https://raw.githubusercontent.com/wiki/netsage-project/netsage-grafana-configs/images/NetSage_Branch_Strategy.png)

The diagram above shows an example of the life-cycle of the various branches. Starting from the top of the diagram you'll see we begin with two branches: the *master* branch and the *1.1.0* release branch. We also want to create a *1.2.0* release branch so the next major release can be developed in parallel. This branch is created from the most recent release branch, *1.1.0*, as shown by the black-dotted line at the top going between the two branches. 

Next, an issue is identified that we want to go in versions 1.1.0 and later of the software. A feature branch is created called *trello-1* from the *1.1.0* branch since it is the lowest version we want to have the feature. The solid blue lines in the diagram shows the life-cycle with the first blue arrow being the branch creation, the second being a commit in the trello-1 branch with the change desired and the final blue arrow being a merge back into the *1.1.0* branch. At that point, the *trello-1* branch is closed and no further changes are made to the branch. This process is followed by three dotted blue lines representing merges of this change to other branches. For now we will just look at the first of these lines. This first dotted blue line is a merge of the change into the 1.2.0 branch since we want this fix in that version as well. It is not strictly required for the merger to happen at this point, but it is highly recommended as doing this often will help identify any potential conflicts early in the development process. Speaking of the *1.2.0* branch, let's look at what was happening over there while we worked on trello-1

Simultaneous to the creation of the *trello-1* branch, a second issue that we only want in version 1.2.0 is identified. A feature branch called *trello-2* is created. The solid red lines follow the lifecycle of this branch with the first being the creation of the branch from 1.2.0 and the second being a commit to the issue branch. With the issue now resolved we want to merge back into the *1.2.0* release branch...but there have been some changes to that branch since we originally created trello-2! In order for there to be a clean merge we first need to merge the latest changes from the *1.2.0* branch into *trello-2* as shown by the dotted blue line. When that is completed, we can cleanly do the reverse direction and merge *trello-2* back into *1.2.0*

Back on branch *1.1.0*, we decide we are now ready for release. First we merge our changes into *master* and create a tag called *v1.1.0*. We then create a new branch called *1.1.1* to hold changes for the next minor revision. The *1.1.0* branch is then closed and no further changes are committed to that branch.

The life-cycle for *1.1.1* is very similar to that of its a predecessor. Another issue is identified and spun into a branch called *trello-3* and then merged back in to the *1.1.1* release branch. When 1.1.1 is ready for release, it is merged into master, tagged *v1.1.1*, and merged into *1.2.0*. At that point 1.1.1 is considered closed as well.

Finally it is identified that we are ready to release *1.2.0*. As such it is merged into master and tagged. Not shown is the fact that *1.2.1* and *1.3.0* release branches are created so the process can continue.

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
