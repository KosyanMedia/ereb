window.STATES =
  'no_connection': 'No connection. Retry every second'
  'stopped': 'Stopped. Click to start'
  'running': 'Running. Click to stop'

window.helpers =
  task_state_for_exit_code: (state) ->
    return 'Running' unless state?
    return 'Success' if state == 0
    'Fail'

window.current_status = 'no_connection'

$(document).ready ->
  defaultHost = 'http://localhost:8888';
  window.SERVER_HOST = Cookies.get('host') or defaultHost

  recentHistory = new RecentHistory('#page_content')
  taskList = new TaskList('#page_content')
  taskForm = new TaskForm('#page_content')
  taskRun = new TaskRun('#page_content')

  $('#host_input').val(window.SERVER_HOST)

  $('#reconnect_button').click ->
    Cookies.set('host', $('#host_input').val())
    window.SERVER_HOST = $('#host_input').val()
    $('#page_content').html('')
    window.current_status = 'no_connection'
    document.location.hash = '#/'

  routes =
    '/': () ->
      recentHistory.render()
    '/task_list': ->
      taskList.render()
    '/tasks/:taskId': (taskId) ->
      taskForm.render(taskId)
    '/tasks/:taskId/runs/:taskRunId': (taskId, taskRunId) ->
      taskRun.render(taskId, taskRunId)

  director.Router(routes).init()

  document.location.hash = '#/' if document.location.hash == ''
