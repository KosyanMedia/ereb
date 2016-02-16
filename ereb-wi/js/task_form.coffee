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
        description: $('#description').val()
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

    $('#cron_schedule').change (e) =>
      schedule = $('#cron_schedule').val()
      prettySchedule = if schedule.split(' ').length == 5 # small validation of cron schedule
        prettyCron.toString(schedule)
      else
        "Cron syntax error"
      $('#pretty_schedule').html(prettySchedule)

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

    prettySchedule = prettyCron.toString(data.config.cron_schedule)

    form =
      """
        <div class="row">
          <div class="col-md-8 col-md-offset-2">
            <form id='task_form'>
              <h2>
                Current task state: #{enabled_state}
              </h2>
              <div class="form-group">
                <div>
                  <input type="hidden" id="task_id" value="#{data.config.name}">
                  <input type="hidden" id="enabled" value="#{data.config.enabled}">
                </div>
                <p>
                  <label for="schedule">Schedule</label>
                  <input type="text" class="form-control" id="cron_schedule"
                    value="#{data.config.cron_schedule}" placeholder="Cron schedule">
                  <code id="pretty_schedule">#{prettySchedule}</code>
                </p>
                <p>
                  <label for="cmd">Cmd</label>
                  <textarea class="form-control" id="cmd">#{data.config.cmd}</textarea>
                </p>
                <p>
                  <label for="description">Description</label>
                  <textarea class="form-control" id="description">#{data.config.description || ''}</textarea>
                </p>
              </div>
              <p>
                <button id="task_form__submit" type="submit" class="btn btn-default">Update</button>
                <button id="task_form__manual_run" class="btn btn-default">Run now!</button>
                <button id="task_form__delete" class="btn btn-danger">Delete</button>
                #{enabled_button}
              </p>
            </form>
          </div>
        </div>
      """

    shell_script_content = if data.config.shell_script_content
      """
      <div class="row">
        <div class="col-md-8 col-md-offset-2">
          <p>
            <label for="shell_script">Contents for file: #{data.config.shell_script_content.filename}</label>
            <textarea id="shell_script" class="form-control" rows="10" readonly>#{data.config.shell_script_content.content}</textarea>
          </p>
        </div>
      </div>
      """
    else
      ''

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
      shell_script_content,
      "<div class='row'>",
      "<br>",
      "<div class='col-md-8 col-md-offset-2'> <table class='table'>",
      rows.join(''),
      "</table></div>",
      "</div>"
    ].join('')

    $(@wrapper).html html

    if shell_script_content
      require("../node_modules/codemirror/lib/codemirror.css")
      require("../node_modules/codemirror/theme/3024-night.css")
      CodeMirror = require("codemirror")

      textarea = $(@wrapper).find('#shell_script')[0]
      PrettyPrint = CodeMirror.fromTextArea(textarea, {
        mode: 'shell'
        theme: '3024-night'
        readOnly: "nocursor"
      })

  fetch: (taskId, callback, useStub=false) ->
    if useStub
      stub =
        config:
          cron_schedule: '* * * * *'
          cmd: 'echo foo'
          name: 'foo',
          enabled: false,
          description: ''
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
