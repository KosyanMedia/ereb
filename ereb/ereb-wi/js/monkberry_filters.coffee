moment = require('moment')
monkberry.filters.pretty_cron = (schedule) =>
  if schedule.split(' ').length == 5 # small validation of cron schedule
    prettyCron.toString(schedule)
  else
    "Cron syntax error"

monkberry.filters.humanize_time = (time) ->  
  moment.duration(time * 1000).humanize()
