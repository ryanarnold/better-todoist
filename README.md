
### Go inside heroku server

`heroku run bash -a better-todoist`

### Push changes to heroku

`git push heroku main`

### Start script

`heroku ps:scale worker=1`

### Stop script

`heroku ps:scale worker=0`
