# Montagu staging

```
vagrant up
```

will bring up two VMs; one called `uat` and one called `science`.

Then, to deploy onto the stage VM of your choice:

```
vagrant ssh uat            # or vagrant ssh science
/vagrant/deploy
```

You will be asked a series of interactive configuration questions. It's 
important that the port you configure Montagu with matches the eventual port
that users will be navigating to. So the port that Vagrant exposes the outside
world must match
