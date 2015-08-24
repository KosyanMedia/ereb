class TaskForm

  constructor: (wrapper) ->
    @wrapper = wrapper

  render: (@taskId) ->
    @fetch @taskId, (data) =>
      @updateTemplate data
      @initEvents()

  initEvents: () ->
    $('#task_form').submit (e) =>
      e.preventDefault()
      data =
        cron_schedule: $('#cron_schedule').val()
        cmd: $('#cmd').val()
      @updateTask @taskId, data, (update_status) =>
        html = if update_status
          """
          <div class="col-md-4 col-md-offset-4 alert alert-success fade in">
            <a href="#" class="close" data-dismiss="alert">×</a>
            Saved
          </div>
          """
        else
          """
          <div class="col-md-4 col-md-offset-4 alert alert-danger fade in">
            <a href="#" class="close" data-dismiss="alert">×</a>
            Error! Check schedule and cmd
          </div>
          """
        $(@wrapper).prepend(html)

    $('#task_form__delete').click (e) =>
      e.preventDefault()
      @deleteTask @taskId, =>
        document.location.hash = '#/task_list'

    $('#task_form__manual_run').click (e) =>
      e.preventDefault()
      @runTask @taskId, =>
        @render(@taskId)

    $('#task_form__enabled_button').click (e) =>
      e.preventDefault()
      data =
        enabled: ! ( $('#enabled').val() == 'true' ) # toggle enabled state
      @updateTask @taskId, data, =>
        @render(@taskId)

  updateTask: (taskId, data, callback) ->
    url = [window.SERVER_HOST, 'tasks', taskId].join('/')
    promise = $.post url, JSON.stringify(data)
    promise.done (response) => callback(true)
    promise.fail (response) => callback(false)

  deleteTask: (taskId, callback) ->
    url = [window.SERVER_HOST, 'tasks', taskId].join('/')
    promise = $.ajax
      url: url
      method: 'DELETE'

    promise.done (response) =>
      callback()

  runTask: (taskId, callback) ->
    url = [window.SERVER_HOST, 'tasks', taskId, 'run'].join('/')
    promise = $.ajax
      url: url

    promise.done (response) =>
      callback()

  updateTemplate: (data) ->
    enabled_button = if data.config.enabled
      """
        <button type="button" id="task_form__enabled_button" class="btn btn-warning navbar-btn" autocomplete="off">
          Disable!
        </button>
      """
    else
      """
        <button type="button" id="task_form__enabled_button" class="btn btn-success navbar-btn" autocomplete="off">
          Enable!
        </button>
      """

    enabled_state = if data.config.enabled
      'Running'
    else
      'Stopped'

    form =
      """
        <div class="row">
          <div class="col-md-6 col-md-offset-3">
            <form id='task_form'>
              <h4> Current task state: #{enabled_state} <h4>
              <div class="form-group">
                <input type="hidden" id="task_id" value="#{data.config.name}">
                <label for="schedule">Schedule</label>
                <input type="text" class="form-control" id="cron_schedule"
                  value="#{data.config.cron_schedule}" placeholder="Cron schedule">
                <label for="cmd">Cmd</label>
                <input type="text" class="form-control" id="cmd"
                  value="#{data.config.cmd}" placeholder="Cmd">
                <input type="hidden" id="enabled" value="#{data.config.enabled}">
              </div>
              <button id="task_form__submit" type="submit" class="btn btn-default">Update</button>
              <button id="task_form__manual_run" class="btn btn-default"> Run now! </button>
              <button id="task_form__delete" class="btn btn-danger">Delete</button>

              #{enabled_button}

            </form>
          </div>
        </div>
      """

    rows = data.runs.map (run) =>
      """
        <tr>
          <td> #{run.started_at} </td>
          <td> #{ if run.finished_at? then run.finished_at else run.current } </td>
          <td> #{ helpers.task_state_for_exit_code(run.exit_code) } </td>
          <td> <a href="#/tasks/#{@taskId}/runs/#{run.id}"> More </a> </td>
        <tr>
      """

    html = [
      form,
      "<div class='row'>",
      "<br>",
      "<div class='col-md-6 col-md-offset-3'> <table class='table'>",
      rows.join(''),
      "</table></div>",
      "</div>"
    ].join('')

    $(@wrapper).html html

  fetch: (taskId, callback, useStub=false) ->
    if useStub
      stub =
        config:
          cron_schedule: '* * * * *'
          cmd: 'echo foo'
          name: 'foo',
          enabled: false
        runs: [
          task_id: 'bar'
          exit_code: 0
          started_at: '2015-07-11 20:05:00'
          finished_at: '2015-07-11 20:10:00'
          current: 'finished'
        ,
          task_id: 'baz'
          started_at: '2015-07-11 20:05:00'
          current: 'started'
        ,
          task_id: 'foo'
          exit_code: -1
          started_at: '2015-07-11 20:05:00'
          finished_at: '2015-07-11 20:10:00'
          current: 'finished'
        ]
      callback(stub)
    else
      url = [window.SERVER_HOST, 'tasks', taskId].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []



module.exports = TaskForm
