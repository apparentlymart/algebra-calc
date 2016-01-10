var jQuery = require('expose?jQuery!jquery');
var angular = require('angular');
var app = angular.module('alg', ['ng']);

var controller = require('./controller.js');
var bodyDirective = require('./body.js');
var mathDirective = require('./math.js');

app.value('angular', angular);
app.controller('algController', controller);
app.directive('body', bodyDirective);
app.directive('math', mathDirective);

module.exports = function (rootElement) {
    angular.bootstrap(rootElement, ['ng', 'alg']);
};
