$ = jQuery = require("jquery");
require("./node_modules/codemirror/lib/codemirror.css")
require("./node_modules/codemirror/theme/3024-night.css")
CodeMirror = require("codemirror")
Cookies = require("./js/cookies.coffee");
moment = require("moment");
moment_range = require("./js/readable_range.coffee");
director = require("director");
prettyCron = require("prettycron");
require("bootstrap-webpack");
monkberry = require('monkberry');
require('monkberry-events');

require("./css/main.scss");
require('./js/monkberry_filters.coffee');
require("./js/main.coffee");

Header = require("./js/blocks/header/header.coffee");
Dashboard = require("./js/blocks/dashboard/dashboard.coffee");
TaskList = require("./js/blocks/task_list/task_list.coffee");
TaskForm = require("./js/blocks/task_form/task_form.coffee");
TaskRun = require("./js/blocks/task_run/task_run.coffee");
