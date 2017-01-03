class TaskForm

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_form.monk'))
    @template = monkberry.render('task_form')
    @initEvents()

  render: (@taskId) ->
    @fetch @taskId, (data) =>
      @data = data
      if @data.runs
        for run in @data.runs
          m1 = moment(run.started_at)
          if run.finished_at == 'None'
            m2 = moment.utc()
          else
            m2 = moment(run.finished_at)
          run['duration'] = moment.preciseDiff(m1, m2)

      @template.appendTo(@wrapper)
      @template.update @data
      # FIXME
      # @highlight()

  highlight: ->
    for el in document.querySelectorAll('[data-role="shell_script"]')
      HightlighJS.highlightBlock(el)

  submitTaskForm: (callback) ->
    data =
      cron_schedule: $('#cron_schedule').val()
      cmd: $('#cmd').val()
      description: $('#description').val()
      group: $('#group').val()
      timeout: $('#timeout').val()
      try_more_on_error: $('#try_more_on_error').is(':checked')

    @updateTask @taskId, data, (update_status) =>
      @data.notification =
        success: update_status == true
      data.enabled = @data.config.enabled
      @data.config = data if update_status
      @template.update @data
      delete @data.notification
      callback() if callback

  initEvents: () ->
    @template.on 'submit', '#task_form', (e) =>
      e.preventDefault()
      @submitTaskForm()

    @template.on 'click', '#task_form__delete', (e) =>
      e.preventDefault()
      @deleteTask @taskId, =>
        document.location.hash = '#/task_list'

    @template.on 'click', '#task_form__manual_run', (e) =>
      e.preventDefault()
      @submitTaskForm =>
        @runTask @taskId, =>
          @render(@taskId)

    @template.on 'click', '#task_form__enabled_button', (e) =>
      e.preventDefault()
      data =
        enabled: ! ( $('#enabled').val() == 'true' ) # toggle enabled state
      @updateTask @taskId, data, =>
        @render(@taskId)

    @template.on 'click', '#task_form__task_run_kill', (e) =>
      e.preventDefault()
      @killTask @taskId, =>
        @render(@taskId)

    @template.on 'change', '#cron_schedule', (e) =>
      @data.config.cron_schedule = $('#cron_schedule').val()
      @template.update @data

  updateTask: (taskId, data, callback) ->
    url = [window.SERVER_HOST, 'tasks', taskId].join('/')
    promise = $.post url, JSON.stringify(data)
    promise.done (response) => callback(true)
    promise.fail (response) => callback(false)

  killTask: (taskId, callback) ->
    url = [window.SERVER_HOST, 'tasks', taskId, 'shutdown'].join('/')
    promise = $.get url
    promise.done (response) => callback()

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

  fetch: (taskId, callback, useStub=false) ->
    if useStub
      stub = require('./stub.coffee')
      callback(stub)
    else
      url = [window.SERVER_HOST, 'tasks', taskId].join('/')
      promise = $.get url

      promise.done (response) ->

        callback JSON.parse(response)

      promise.fail (response) ->
        callback []



module.exports = TaskForm
