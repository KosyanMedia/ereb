window.getStatus = (callback, useStub=false) =>
  if useStub
    stub =
      state: 'running'
      next_run: 4345.1007
      next_tasks: [
        cron_schedule: '* * * * *'
        name: 'bar'
        cmd: 'echo bar'
      ,
        cron_schedule: '* * * * *'
        name: 'foo'
        cmd: 'echo foo'
      ,
        cron_schedule: '* * * * *'
        name: 'baz'
        cmd: 'echo baz'
      ]
      planned_task_run_uuids: [
        "1a282d86-2b37-4332-a781-38b24eefc8e9"
      ]
    callback(stub)
  else
    url = [window.SERVER_HOST, 'status'].join('/')
    promise = $.get url

    promise.done (response) ->
      callback JSON.parse(response)

    promise.fail (response) ->
      callback
        state: 'no_connection'
        next_run: -1
        next_tasks: []

window.updateHeader = () =>
  getStatus (status_response) =>
    window.current_status = current_status = status_response.state

    status_button_text = window.STATES[current_status]
    status_button_class = if status_response.state == 'running'
      'btn-success'
    else
      'btn-warning'

    status_button = $('#running_button')
    status_button.text(status_button_text)
    status_button.removeClass('btn-success btn-warning')
    status_button.addClass(status_button_class)

    if current_status == 'no_connection'
      status_button.attr('disabled', true)
      $('#next_run_txt').html('')
    else
      status_button.attr('disabled', false)
      now = moment()
      next_run_time = moment().add(status_response.next_run, 'seconds')
      next_run_task_links = status_response.next_tasks.map (t) ->
        "<a href='#'> #{t.name} </a>"

      next_run_text = """
        Next run of tasks
        #{next_run_task_links}
        in #{moment.preciseDiff(now, next_run_time)}
      """

      $('#next_run_txt').html(next_run_text)


$(document).ready ->
  $('#running_button').click ->
    url = if window.current_status == 'stopped'
      [window.SERVER_HOST, 'status', 'start'].join('/')
    else
      [window.SERVER_HOST, 'status', 'stop'].join('/')
    $(@).attr('disabled', true)
    $.get url

setInterval =>
  updateHeader()
, 1000
