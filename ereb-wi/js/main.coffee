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

defaultHost = "http://#{document.location.hostname}"
defaultPort = if window.DEFAULT_CONFIG then window.DEFAULT_CONFIG.port else 8888
window.SERVER_HOST = Cookies.get('host') or "#{defaultHost}:#{defaultPort}"

$(document).ready ->
  $('#header_info').html("Ereb for great future! #{window.DEFAULT_CONFIG.version}")

  header = new Header(document.getElementById('header'))
  dashboard = new Dashboard(document.getElementById('page_content'))
  taskList = new TaskList(document.getElementById('page_content'))
  taskForm = new TaskForm(document.getElementById('page_content'))
  taskRun = new TaskRun(document.getElementById('page_content'))

  $('#host_input').val(window.SERVER_HOST)

  routes =
    '/': () ->
      $('#page_content').html('')
      dashboard.render()
    '/task_list': ->
      taskList.render()
    '/tasks/:taskId': (taskId) ->
      taskForm.render(taskId)
    '/tasks/:taskId/runs/:taskRunId': (taskId, taskRunId) ->
      taskRun.render(taskId, taskRunId)

  director.Router(routes).init()

  document.location.hash = '#/' if document.location.hash == ''
