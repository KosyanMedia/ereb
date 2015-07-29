class TaskList
  defaultSchedule: '* */1 * * *'
  defaultCmd: 'echo'

  constructor: (wrapper) ->
    @wrapper = wrapper

  render: (taskId, taskRunId) ->
    @fetch taskId, taskRunId, (data) =>
      @updateTemplate data
      @initEvents()

  initEvents: ->
    $('#new_task_form__submit').click (e) =>
      console.log(@)
      e.preventDefault()
      newTaskName = $('#new_task_name').val()
      unless newTaskName == ''
        @createTask newTaskName, =>
          document.location.hash = ['#/tasks', newTaskName].join('/')

  updateTemplate: (data) ->
    rows = data.map (task) =>
      """
        <tr>
          <td> <a href="#/tasks/#{task.name}"> #{task.name} </a> </td>
          <td> #{task.cron_schedule} </td>
          <td> #{task.cmd} </td>
        </td>
      """

    html =
      """
        <div class="row">
          <div class="col-md-6 col-md-offset-3">
            <h4> Task list </h4>
            <table class="table">
            <thead>
              <tr>
                <th> Name </th>
                <th> Schedule </th>
                <th> Cmd </th>
              </tr>
            </thead>
              #{ rows.join('') }
            </table>
          </div>
        </div>

        <div class="row">
          <div class="col-md-4 col-md-offset-3">
            <form id='task_form'>
              <div class="form-group">
                <label for="task_name">New task name</label>
                <input type="text" class="form-control" id="new_task_name" placeholder="Name">
              </div>
              <butto  n id="new_task_form__submit" type="submit" class="btn btn-default">Create</button>
            </form>
          </div>
        </div>
      """

    $(@wrapper).html html

  fetch: (taskId, taskRunId, callback, useStub=false) ->
    if useStub
      stub = [
        cron_schedule: '* * * * *'
        cmd: 'echo foo'
        name: 'foo'
      ,
        cron_schedule: '* * * * *'
        cmd: 'echo bar'
        name: 'bar'
      ]
      callback(stub)
    else
      url = [window.SERVER_HOST, 'tasks'].join('/')
      promise = $.get url

      promise.done (response) ->
        callback JSON.parse(response)

      promise.fail (response) ->
        callback []

  createTask: (name, callback) ->
    url = [window.SERVER_HOST, 'tasks'].join('/')
    promise = $.post url, JSON.stringify
      task_id: name
      cmd: [@defaultCmd, name].join(' ')
      cron_schedule: @defaultSchedule

    promise.done (response) ->
      callback()


module.exports = TaskList
