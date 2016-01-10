var MathQuill = require('imports?jQuery=jquery!exports?MathQuill!./mathquill.js');
var mathquillCss = require('../styles/mathquill.css');

module.exports = [
    'angular',
    '$timeout',
    function (angular, $timeout) {
        MathQuill.interfaceVersion(1);

        return {
            restrict: 'EA',
            require: ['^body', 'ngModel'],
            link: function (scope, iElement, iAttr, ctrls) {
                var bodyCtrl = ctrls[0];
                var ngModel = ctrls[1];
                var container;
                var quill;
                var id = iAttr.id;
                ngModel.$render = function () {
                    scope.$evalAsync(function () {
                        if (quill) {
                            quill.latex(ngModel.$viewValue);
                        }
                    });
                };

                scope.$watch(
                    function () {
                        return iAttr.readonly !== undefined;
                    },
                    function (readOnly) {
                        if (container) {
                            container.remove();
                            container = undefined;
                        }

                        var container = angular.element('<div></div>');
                        iElement.append(container);
                        if (readOnly) {
                            quill = MathQuill.StaticMath(container[0]);
                        }
                        else {
                            quill = MathQuill.MathField(container[0], {
                                handlers: {
                                    edit: function (quill) {
                                        ngModel.$setViewValue(quill.latex());
                                    },

                                    /*
                                     // FIXME: For some reason MathQuill
                                     // doesn't notify us of this.
                                    enter: function (quill) {
                                        iElement.trigger('submit');
                                    }*/
                                },
                                spaceBehavesLikeTab: true,
                                restrictMismatchBrackets: true,
                                supSubsRequireOperand: true,
                                autoSubscriptNumerals: true,
                                charsThatBreakOutOfSupSub: '='
                            });

                            // Hook into pressing enter directly because
                            // MathQuill's 'enter' event doesn't seem to work.
                            container.bind('keydown', function (evt) {
                                if (evt.keyCode === 13 || evt.keyCode === 10) {
                                    iElement.trigger('submit');
                                }
                            });
                        }
                        if (id) {
                            bodyCtrl.registerQuill(id, quill);
                        }
                        ngModel.$render();
                    }
                );
            }
        };
    }
];
