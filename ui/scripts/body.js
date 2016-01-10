var template = require('html!../templates/body.html');

var apiUrl = (
    'https://i75har4835.execute-api.us-west-2.amazonaws.com/prod/solve'
);

var controller = [
    '$scope',
    '$http',
    '$timeout',
    '$q',
    'angular',
    function bodyController($scope, $http, $timeout, $q, angular) {
        var quills = {};
        var cancelReq;
        var editTimeout;

        $scope.loading = false;
        $scope.statements = [];
        $scope.knowns = {};
        $scope.unknowns = {};
        $scope.newStatement = '';

        function beginUpdate() {
            if (editTimeout) {
                $timeout.cancel(editTimeout);
            }
            if (cancelReq) {
                cancelReq.resolve(true);
            }

            var splitStatements = $scope.statements.map(
                function (statement) {
                    return statement.split('=');
                }
            );

            if (splitStatements.length < 1) {
                return;
            }

            var cancelReq = $q.defer();
            $http.post(
                apiUrl,
                {
                    statements: splitStatements
                },
                {
                    timeout: cancelReq.promise
                }
            ).then(completeUpdate);
        }

        function completeUpdate(res) {
            var data = res.data;

            if (! data.known) {
                if (data.errorMessage) {
                    console.error(data.errorMessage);
                }
                return;
            }

            var knownKeys = Object.keys(data.known);
            knownKeys.sort();
            var unknownKeys = Object.keys(data.unknown);
            unknownKeys.sort();

            $scope.knowns = [];
            $scope.unknowns = [];

            var symbol, values, parts, possibility, i, j;

            for (i = 0; i < knownKeys.length; i++) {
                symbol = knownKeys[i];
                values = data.known[symbol].results;

                parts = [symbol];

                for (j = 0; j < values.length; j++) {
                    possibility = values[j];
                    var floatVal = possibility['float'];
                    var rationalVal = possibility.rational;

                    floatVal = floatVal.replace(
                        /^(\d+)\.0$/,
                        function (match, num) {
                            return num;
                        }
                    );

                    if (floatVal !== rationalVal) {
                        parts.push(rationalVal);
                    }
                    parts.push(floatVal);
                }

                $scope.knowns.push(parts.join(' = '));
            }

            for (i = 0; i < unknownKeys.length; i++) {
                symbol = unknownKeys[i];
                values = data.unknown[symbol].resolutions;

                parts = [symbol];

                for (j = 0; j < values.length; j++) {
                    possibility = values[j];
                    var solutions = possibility.solutions;
                    parts.push(solutions.join(' \\textrm{or} '));
                }

                $scope.unknowns.push(parts.join(' = '));
            }

            console.log(data.unknown);
        }

        $scope.$watchCollection(
            'statements',
            beginUpdate
        );

        $scope.addNewStatement = function addNewStatement() {
            $scope.statements.push($scope.newStatement);
            $scope.newStatement = '';
            var newElem = angular.element('#new div');
            if (quills.newStatement) {
                quills.newStatement.focus();
            }
        };

        this.registerQuill = function registerQuill(id, quill) {
            quills[id] = quill;
        };
    }
];

module.exports = [
    function () {
        return {
            template: template,
            controller: controller
        };
    }
];
