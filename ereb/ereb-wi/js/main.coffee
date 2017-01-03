defaultHost = "http://#{document.location.hostname}"
defaultPort = if window.DEFAULT_CONFIG then window.DEFAULT_CONFIG.port else 8888
window.SERVER_HOST = Cookies.get('host') or "#{defaultHost}:#{defaultPort}"

$(document).ready ->
  header = new Header(document.getElementById('header'))
  dashboard = new Dashboard(document.getElementById('page_content'))
  taskList = new TaskList(document.getElementById('page_content'))
  failedTasks = new FailedTasks(document.getElementById('page_content'))
  taskForm = new TaskForm(document.getElementById('page_content'))
  taskRun = new TaskRun(document.getElementById('page_content'))

  routes =
    '/': () ->
      $('#page_content').html('')
      dashboard.render()
    '/task_list': ->
      $('#page_content').html('')
      taskList.render()
    '/failed_tasks': ->
      $('#page_content').html('')
      failedTasks.render()
    '/tasks/:taskId': (taskId) ->
      $('#page_content').html('')
      taskForm.render(taskId)
    '/tasks/:taskId/runs/:taskRunId': (taskId, taskRunId) ->
      $('#page_content').html('')
      taskRun.render(taskId, taskRunId)

  director.Router(routes).init()

  document.location.hash = '#/' if document.location.hash == ''
