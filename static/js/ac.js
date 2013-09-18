var app = angular.module('myApp', []);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
    });

function SiteCtrl($scope, $http) {

    $scope.data = []

    $scope.loadData = function(code) {

        var httpRequest = $http({
            method: 'GET',
            url: '/api/site/' + code + '/10'
        }).success(function(data, status) {
            $scope.data = data.data;
        });
    };
}
