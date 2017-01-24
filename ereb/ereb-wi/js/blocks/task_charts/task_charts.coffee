class TaskCharts

  constructor: (wrapper) ->
    @wrapper = wrapper
    monkberry.mount(require('./task_charts.monk'))
    @template = monkberry.render('task_charts')


  render: (taskId, taskRunId) ->
    @fetch (tasks) =>
      tasks_by_tab = {}
      for task in tasks        
        group = (task.group || 'Default').replace(' ', '_')
        tasks_by_tab[group] ||= []
        tasks_by_tab[group].push(task)

      @template.appendTo(@wrapper)
      @template.update
        tasks_by_tab: tasks_by_tab

      $($('.js-tabs')[0]).tab('show')

  fetch: (callback) ->
    url = [window.SERVER_HOST, 'tasks'].join('/')
    promise = $.get url

    promise.done (response) ->
      callback JSON.parse(response)

    promise.fail (response) ->
      callback []


module.exports = TaskCharts
